from strategies.rules.logic import Logic
from talib.abstract import MA
import pandas as pd


class ITFollowLogic(Logic):
    strategy_name = "ITFollow"
    trader_code = "001"
    mature_day = 25
    stop_loss = 0.06

    def _load_data(self):
        self.it = self.get_data("investment_trust")
        self.issued_shares = self.get_data("issued_shares")
        self.twii_c = self.get_data("twii_close", no_sid=True)
        self.twii_ma25 = self.twii_c[['twii']].apply(lambda c: MA(c, timeperiod=25))

    def _cal_indicators(self):
        # 投信買超 200 張
        cond1 = self.it / 1e3 > 200

        # 公司市值小於 10 億
        cond2 = self.issued_shares * 10 < 1e9

        twii_cond = pd.DataFrame(~(
                (self.twii_c < self.twii_ma25) &
                (self.twii_ma25 < self.twii_ma25.shift(1))
        ))

        self.select = (cond1 & cond2).apply(lambda r: r & twii_cond.loc[r.name, 'twii'], axis=1)

    def buy_logic(self, sid, date):
        return sid in self.selected[date]

    def sell_logic(self, sid, date, **kwargs):
        cond1 = kwargs['holding_days'] >= 30
        return any([cond1])
