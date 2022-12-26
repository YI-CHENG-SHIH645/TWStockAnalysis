from data.database.interface import create_table, PsqlConnect, \
                                    execute_sql, res_to_df
from strategies.rules.logic import Logic
from collections import defaultdict
import datetime as dt
import numpy as np


def _get_pnl(open_price, sell_price, return_tax_fee=False):
    tax = 0.003 * sell_price
    fee = 0.001425 * 0.6 * (sell_price + open_price)
    pnl = round((sell_price - open_price -
                 tax - fee) / open_price * 100, 2)
    if return_tax_fee:
        return pnl, tax, fee
    else:
        return pnl


# 2nd parallelize this
def _trade(cur, logic, tid: int, sid: str, open_price, holding_days, last_date_signal, today):
    execute_sql('update_last_check', (today, tid), cur=cur, return_result=False)
    o, c = logic.get('adj_o'), logic.get('adj_c')
    last_date = c.index[-1]
    for i, date in enumerate(c.index):
        if date < logic.start_date or i < logic.mature_day:
            continue
        if open_price is not None and not np.isnan(open_price):
            if date != last_date:
                holding_days += 1
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
                execute_sql(
                    'update_record_on_sell', (sell_date, sell_price, holding_days, pnl, tax, fee, tid),
                    cur=cur,
                    return_result=False
                )
                # 加入一筆新的追蹤，未開倉
                open_price, holding_days = None, 0
                tid = execute_sql(
                    'add_trading_record',
                    (sid, logic.strategy_name, logic.trader_code, 0, today),
                    cur=cur
                )[0][0][0]
                open_price = None
        else:
            if logic.buy_logic(sid, date):
                if date != last_date:
                    buy_date, buy_price = c.index[i+1], o.iloc[i+1][sid]
                    execute_sql(
                        'update_record_on_buy',
                        (buy_date, buy_price, "long", 1, tid),
                        cur=cur,
                        return_result=False
                    )
                    open_price, holding_days = buy_price, 1
                # else:
                #     last_date_signal["buy"].append(sid)
    if open_price is not None and not np.isnan(open_price):
        execute_sql('update_holding_days', (holding_days, tid), cur=cur, return_result=False)
        pnl = _get_pnl(open_price, c.iloc[-1][sid])
        execute_sql('update_pnl', (pnl, tid), cur=cur, return_result=False)


# cumtime: 42.6s
def strategy(logic_cls: Logic.__class__, args, start_date="2013-01-01", skip_select=False):
    with PsqlConnect() as (conn, cur):
        create_table(cur, "trading_record")
        if args.new_start:
            execute_sql('drop_history_record', (logic_cls.strategy_name,), return_result=False)
        records = res_to_df(*execute_sql('get_trading_record', (logic_cls.strategy_name, ), cur=cur))

        if not len(records):
            start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = records.loc[0, "last_check"]

        last_date_signal = defaultdict(list)
        logic = logic_cls(start_date, skip_select=skip_select)
        last_date_signal['strategy_name'] = logic.strategy_name
        today = logic.c.index[-1]
        last_date_signal['date'] = today.strftime("%Y-%m-%d")
        for sid in logic.c:
            if sid not in records['sid'].values:
                params = (sid, logic.strategy_name, logic.trader_code, 0, today)
                tid = execute_sql('add_trading_record', params, cur=cur)[0][0][0]
                open_price, holding_days = None, 0
            else:
                tid, open_price, holding_days = records.loc[records.sid == sid, ["tid", "open_price", "holding_days"]].values[0]
            _trade(cur, logic, int(tid), sid, open_price, int(holding_days), last_date_signal, today)
        conn.commit()
        holdings = res_to_df(*execute_sql('get_holding', (logic.strategy_name, ), cur=cur))
        print('signals of {} till {} ---> OK!'.format(logic.strategy_name, today.strftime("%Y-%m-%d")))
    last_date_signal['hold'].extend(holdings['sid'].values)
    last_date_signal['buy'].extend(logic.selected[logic.c.index[-1]])
    last_date_signal['sell'].extend([])
    return last_date_signal
