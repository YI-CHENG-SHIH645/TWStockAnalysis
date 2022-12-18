import data
import pandas as pd
import numpy as np
from strategies.rules.money_distribution.utils \
    import get_history_record, cal_summary


FEE = 1.425e-3 * 0.6
TAX = 3e-3


class MoneyDistribution:
    # money per unit: thousand (ex: 1000 = 1 million)
    def __init__(self, strategy_name: str, init_balance=1e3):
        # 取得策略名稱對應的歷史交易推薦
        history_record = get_history_record(strategy_name)

        # 歷史交易推薦第一筆的日期
        self.start_date = history_record['open_date'].min()

        # 根據推薦買入日期分群
        self.start_date_grps = history_record.groupby('open_date')

        # 根據賣出推薦日期分群
        self.end_date_grps = history_record.groupby('close_date')

        self.history_record = history_record

        # 取得收盤價並且計算調整收盤
        self.c = data.get("close").ffill()
        adj_ratio = data.get_adj_ratio(self.c.index, self.c.columns)
        self.adjc = self.c * adj_ratio

        # 給定起始金額
        self.init_balance = init_balance

        # 手上持有現金
        self.money = self.init_balance

        self.strategy_name = strategy_name

        # 現在手上持有的股票代號是對應到交易明細的哪一筆
        self.holding = {}  # sid: tid

        # 每日日期 對應 總價值
        self.portfolio_value = {}  # date: portfolio value

        # 收集所有交易明細的id, 用來呈現所有有實際以金錢交易的交易明細
        self.record_id = []

        self.today = None

    def get_shares(self, tid):
        s = self.history_record.tid.isin([tid])
        return self.history_record.loc[s[s].index, "shares"].values[0]

    def set_shares(self, tid, num):
        s = self.history_record.tid.isin([tid])
        self.history_record.loc[s[s].index, "shares"] = num

    def cal_value(self):
        # cash on hand
        value = self.money
        for sid in self.holding:
            close = self.adjc.loc[self.today, sid]
            assert not np.isnan(close)
            value += close * self.get_shares(self.holding[sid])
        return value

    def _record_value(self):
        value = self.cal_value()
        assert not np.isnan(value)
        self.portfolio_value.update({str(self.today): value})

    def buy(self, tid, sid, open_price, shares):
        assert self.money >= open_price * shares * (1+FEE)
        self.money -= open_price * (1 + FEE) * shares
        self.record_id.append(tid)
        self.set_shares(tid, shares)
        self.holding.update({sid: tid})

    def sell(self, tid, sid, close_price, shares):
        assert shares <= self.get_shares(tid)
        self.money += close_price * (1 - TAX - FEE) * shares
        self.holding.pop(sid)

    def get_buy_recommendation(self):
        # today no recommendation
        if self.today not in self.start_date_grps.groups.keys():
            return pd.DataFrame()
        # get recommendation list
        df = self.start_date_grps.get_group(self.today)
        # it's impossible to purchase even the cheapest one
        if self.money < df.open_price.min() * (1 + FEE):
            return pd.DataFrame()

        return df

    def get_sell_recommendation(self):
        # today no recommendation
        if self.today not in self.end_date_grps.groups.keys():
            return pd.DataFrame()
        # get recommendation list
        df = self.end_date_grps.get_group(self.today)
        # whether i have stock on my hand that's also on the recommendation list
        sell = set(self.holding.keys()).intersection(set(df.sid))
        df = df[df.sid.isin(sell)]

        return df

    def _get_all_records(self):
        records_df = self.history_record[self.history_record.tid.isin(self.record_id)].copy()
        records_df['open_price'] = records_df['open_price'].round(2)
        records_df['close_price'] = records_df['close_price'].round(2)
        trading_records = {
            "strategy_name": self.strategy_name,
            "records": list(records_df.astype({"open_date": str, "close_date": str, "last_check": str})
                            .fillna("None")
                            .to_dict('index')
                            .values())
        }

        return trading_records

    def try_to_buy(self):
        raise NotImplementedError

    def try_to_sell(self):
        raise NotImplementedError

    def reaction_after_sell(self):
        pass

    def cal(self):
        for date in self.adjc.index:
            if date < self.start_date:
                continue
            self.today = date
            self.try_to_sell()
            self._record_value()
            self.reaction_after_sell()
            self.try_to_buy()

        print('money distribution of {} till {} ---> OK!'.format(self.strategy_name,
                                                                 self.adjc.index[-1].strftime("%Y-%m-%d")))
        summary = cal_summary(self.strategy_name,
                              self.portfolio_value,
                              self.init_balance,
                              self.holding,
                              self.money)
        trading_records = self._get_all_records()

        return summary, trading_records
