import pandas as pd

from data.database.interface import create_table, PsqlConnect, \
                                    execute_sql, res_to_df
from strategies.rules.logic import Logic
from strategies.cpp_acc.core import print_hi
from collections import defaultdict
import datetime as dt
import numpy as np
from data.database.interface import upsert


def _get_pnl(open_price, sell_price, return_tax_fee=False):
    tax = 0.003 * sell_price
    fee = 0.001425 * 0.6 * (sell_price + open_price)
    pnl = round((sell_price - open_price -
                 tax - fee) / open_price * 100, 2)
    if return_tax_fee:
        return pnl, tax, fee
    else:
        return pnl


# TODO 2nd parallelize this
def _trade(dic_records, logic, tid: int, sid: str, open_price,
           holding_days, last_date_signal, today, available_tid):
    # execute_sql('update_last_check', (today, tid), cur=cur, return_result=False)
    dic_records[tid].update({'last_check': today})

    o, c = logic.get('adj_o'), logic.get('adj_c')
    last_date = c.index[-1]
    for i, date in enumerate(c.index):
        if date < logic.start_date or i < logic.mature_day:
            continue
        if open_price is not None and not np.isnan(open_price):
            holding_days += date != last_date
            if logic.sell_logic(sid, date, open_price=open_price, holding_days=holding_days):
                if date == last_date:
                    last_date_signal["sell"].append(sid)
                    break
                sell_price = o.iloc[i+1][sid]  # data['open'][i + 1]
                pnl, tax, fee = _get_pnl(open_price, sell_price, return_tax_fee=True)
                tax = round(tax * 1000, 2)
                fee = round(fee * 1000, 2)

                sell_date = c.index[i+1]  # data['date'][i + 1]
                # 賣出 同時取消追蹤
                # execute_sql(
                #     'update_record_on_sell', (sell_date, sell_price, holding_days, pnl, tax, fee, tid),
                #     cur=cur,
                #     return_result=False
                # )
                dic_records[tid].update({
                    'close_date': sell_date,
                    'close_price': sell_price,
                    'holding_days': holding_days,
                    'pnl': pnl,
                    'tax': tax,
                    'fee': fee
                })

                # 加入一筆新的追蹤，未開倉
                open_price, holding_days = None, 0
                # tid = execute_sql(
                #     'add_trading_record',
                #     (sid, logic.strategy_name, logic.trader_code, 0, today),
                #     cur=cur
                # )[0][0][0]
                r = {
                    'sid': sid,
                    'strategy_name': logic.strategy_name,
                    'trader_code': logic.trader_code,
                    'holding_days': 0,
                    'last_check': today,
                    'open_price': None,
                }
                tid = available_tid
                dic_records[tid] = r
                available_tid += 1
        else:
            if logic.buy_logic(sid, date):
                if date != last_date:
                    buy_date, buy_price = c.index[i+1], o.iloc[i+1][sid]
                    # execute_sql(
                    #     'update_record_on_buy',
                    #     (buy_date, buy_price, "long", 1, tid),
                    #     cur=cur,
                    #     return_result=False
                    # )
                    r = {
                        'open_date': buy_date,
                        'open_price': buy_price,
                        'long_short': "long",
                        'shares': 1
                    }
                    dic_records[tid].update(r)
                    open_price, holding_days = buy_price, 1
                # else:
                #     last_date_signal["buy"].append(sid)
    if open_price is not None and not np.isnan(open_price):
        # execute_sql('update_holding_days', (holding_days, tid), cur=cur, return_result=False)
        pnl = _get_pnl(open_price, c.iloc[-1][sid])
        # execute_sql('update_pnl', (pnl, tid), cur=cur, return_result=False)
        dic_records[tid].update({'holding_days': holding_days, 'pnl': pnl})

    return available_tid


def strategy(logic_cls: Logic.__class__, args, start_date="2013-01-01", skip_select=False):
    with PsqlConnect() as (conn, cur):
        create_table(cur, "trading_record")
        conn.commit()
        if args.new_start:
            execute_sql('drop_history_record', (logic_cls.strategy_name,), cur=cur, return_result=False)
        conn.commit()
        records = res_to_df(*execute_sql('get_trading_record', (logic_cls.strategy_name, ), cur=cur))
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

    for sid in logic.c:
        if sid not in sid2tid:
            r = {
                'sid': sid,
                'strategy_name': logic.strategy_name,
                'trader_code': logic.trader_code,
                'holding_days': 0,
                'last_check': today,
                'open_price': None,
             }
            tid = available_tid
            dic_records[tid] = r
            available_tid += 1
            # params = (sid, logic.strategy_name, logic.trader_code, 0, today)
            # tid = execute_sql('add_trading_record', params, cur=cur)[0][0][0]
        else:
            tid = sid2tid[sid]
            r = dic_records[sid2tid[sid]]

        available_tid = _trade(dic_records, logic, tid,
                               sid, r['open_price'], int(r['holding_days']),
                               last_date_signal, today, available_tid)

    new_records = pd.DataFrame.from_dict(dic_records, orient='index')\
                              .rename_axis('tid').reset_index()
    with PsqlConnect() as (conn, cur):
        upsert(cur, 'trading_record', ['tid'], new_records.columns.tolist()[1:], new_records)
        conn.commit()
        holdings = res_to_df(*execute_sql('get_holding', (logic.strategy_name, ), cur=cur))
    print('signals of {} till {} ---> OK!'.format(logic.strategy_name, today.strftime("%Y-%m-%d")))
    last_date_signal['hold'].extend(holdings['sid'].values)
    last_date_signal['buy'].extend(logic.selected[logic.c.index[-1]])
    last_date_signal['sell'].extend([])
    print_hi()
    return last_date_signal
