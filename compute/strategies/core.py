from collections import defaultdict
import datetime as dt
import numpy as np
import pandas as pd
from data.database.interface import create_table, PsqlConnect, \
    execute_sql, res_to_df, upsert
from strategies.rules.logic import Logic
from strategies.cpp_acc.core import trade_on_sids


def _get_pnl(open_price: float,
             sell_price: float,
             return_tax_fee=False):
    tax = 0.003 * sell_price
    fee = 0.001425 * 0.6 * (sell_price + open_price)
    pnl = round((sell_price - open_price -
                 tax - fee) / open_price * 100, 2)
    if return_tax_fee:
        return pnl, tax, fee
    else:
        return pnl


def sell_logic(hd, hd_th, adj_c, adj_c_ma20):
    cond = (hd >= hd_th) or adj_c < adj_c_ma20

    return cond


def _trade(dic_records: dict,
           tid: int,
           sid: str,
           open_price: float,
           holding_days: int,
           holding_days_th: int,
           last_date_signal: dict,
           today: dt.datetime,
           available_tid: int,
           o: np.ndarray,
           c: np.ndarray,
           ma20: np.ndarray,
           dates: np.ndarray,
           selected: dict,
           strategy_name: str,
           trader_code: str):
    last_date = dates[-1]
    for i, date in enumerate(dates):
        if np.isfinite(open_price):
            holding_days += date != last_date
            if sell_logic(holding_days, holding_days_th, c[i], ma20[i]):
                if date == last_date:
                    last_date_signal["sell"].append(sid)
                    break
                sell_price = o[i + 1]
                pnl, tax, fee = _get_pnl(open_price, sell_price, return_tax_fee=True)
                tax = round(tax * 1000, 2)
                fee = round(fee * 1000, 2)

                sell_date = dates[i + 1]
                # 賣出 同時取消追蹤
                dic_records[tid].update({
                    'close_date': sell_date,
                    'close_price': sell_price,
                    'holding_days': holding_days,
                    'pnl': pnl,
                    'tax': tax,
                    'fee': fee
                })

                # 加入一筆新的追蹤，未開倉
                open_price, holding_days = np.nan, 0
                r = {
                    'sid': sid,
                    'strategy_name': strategy_name,
                    'trader_code': trader_code,
                    'holding_days': 0,
                    'last_check': today,
                    'open_price': np.nan,
                }
                tid = available_tid
                dic_records[tid] = r
                available_tid += 1
        else:
            if sid in selected[date]:
                if date != last_date:
                    buy_date, buy_price = dates[i + 1], o[i + 1]
                    r = {
                        'open_date': buy_date,
                        'open_price': buy_price,
                        'long_short': "long",
                        'shares': 1
                    }
                    dic_records[tid].update(r)
                    open_price, holding_days = buy_price, 1
    if np.isfinite(open_price):
        pnl = _get_pnl(open_price, c[-1])
        dic_records[tid].update({'holding_days': holding_days, 'pnl': pnl})

    return available_tid


def _trade_on_sids(sids: np.ndarray,
                   o: dict,
                   c: dict,
                   ma20: dict,
                   dates: np.ndarray,
                   selected: dict,
                   holding_days_th: int,
                   dic_records: dict,
                   last_date_signal: dict,
                   sid2tid: dict,
                   today: dt.datetime,
                   available_tid: int,
                   strategy_name: str,
                   trader_code: str):
    for sid in sids:
        if sid not in sid2tid:
            r = {
                'sid': sid,
                'strategy_name': strategy_name,
                'trader_code': trader_code,
                'holding_days': 0,
                'last_check': today,
                'open_price': np.nan,
            }
            tid = available_tid
            dic_records[tid] = r
            available_tid += 1
        else:
            tid = sid2tid[sid]
            r = dic_records[sid2tid[sid]]
        dic_records[tid].update({'last_check': today})
        open_price = np.array(r['open_price'], dtype=float).item()
        holding_days = int(r['holding_days'])
        available_tid = _trade(dic_records, tid,
                               sid, open_price, holding_days, holding_days_th,
                               last_date_signal, today, available_tid,
                               o[sid], c[sid], ma20[sid], dates, selected,
                               strategy_name, trader_code)


def strategy(logic_cls: Logic.__class__, args, start_date="2013-01-01", skip_select=False):
    with PsqlConnect() as (conn, cur):
        create_table(cur, "trading_record")
        conn.commit()
        if args.new_start:
            execute_sql('drop_history_record', (logic_cls.strategy_name,), cur=cur, return_result=False)
        conn.commit()
        records = res_to_df(*execute_sql('get_trading_record', (logic_cls.strategy_name,), cur=cur))
        max_tid = execute_sql('get_max_tid', cur=cur)[0][0][0]
    if not len(records):
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date = records.loc[0, "last_check"]

    last_date_signal = defaultdict(list)
    logic = logic_cls(start_date, skip_select=skip_select)
    last_date_signal['strategy_name'] = logic.strategy_name
    today = logic.c.index[-1]
    last_date_signal['date'] = today.strftime("%Y-%m-%d")
    available_tid = 0 if max_tid is None else max_tid + 1
    sid2tid = dict(zip(records.sid, records.tid))
    records = records.set_index('tid')
    dic_records = defaultdict(dict, records.to_dict(orient='index'))

    o, c = logic.get('adj_o'), logic.get('adj_c')
    o = o.iloc[logic.mature_day:].truncate(before=logic.start_date)
    c = c.iloc[logic.mature_day:].truncate(before=logic.start_date)
    dates = c.index.values

    ma20 = getattr(logic, "ma20", np.full_like(c.values.T, np.nan, dtype=float))
    if not isinstance(ma20, np.ndarray):
        ma20 = ma20.iloc[logic.mature_day:].truncate(before=logic.start_date)
        ma20 = ma20.values.T

    # TODO: parallelize this
    trade_on_sids(c.columns.values,
                  dict(zip(o.columns, o.values.T)),
                  dict(zip(c.columns, c.values.T)),
                  dict(zip(c.columns, ma20)),
                  pd.to_datetime(dates),
                  logic.selected,
                  logic.holding_days_th,
                  dic_records,
                  last_date_signal,
                  sid2tid,
                  pd.to_datetime(today),
                  available_tid,
                  logic.strategy_name,
                  logic.trader_code)

    new_records = pd.DataFrame.from_dict(dic_records, orient='index') \
        .rename_axis('tid').reset_index()
    with PsqlConnect() as (conn, cur):
        upsert(cur, 'trading_record', ['tid'], new_records.columns.tolist()[1:], new_records)
        conn.commit()
        holdings = res_to_df(*execute_sql('get_holding', (logic.strategy_name,), cur=cur))
    print('signals of {} till {} ---> OK!'.format(logic.strategy_name, today.strftime("%Y-%m-%d")))
    last_date_signal['hold'].extend(holdings['sid'].values)
    last_date_signal['buy'].extend(logic.selected[logic.c.index[-1]])
    last_date_signal['sell'].extend([])
    return last_date_signal
