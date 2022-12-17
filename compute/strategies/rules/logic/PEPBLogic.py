from strategies.rules.logic import Logic
from talib.abstract import MA
import pandas as pd


class PEPBLogic(Logic):
    strategy_name = "PEPB"
    trader_code = "001"
    mature_day = 25
    stop_loss = 0.06

    def _load_data(self):
        self.pe = self.get_data("pe")
        self.pb = self.get_data("pb")
        self.twii_c = self.get_data("twii_close", no_sid=True)
        self.twii_ma25 = self.twii_c[['twii']].apply(lambda c: MA(c, timeperiod=25))

    def _cal_indicators(self):

        # 本益比 小於 13
        cond1 = self.pe < 13

        # 股價淨值比 小於 0.7
        cond2 = self.pb < 0.7

        twii_cond = pd.DataFrame(~(
                (self.twii_c < self.twii_ma25) &
                (self.twii_ma25 < self.twii_ma25.shift(1))
        ))

        self.select = (cond1 & cond2).apply(lambda r: r & twii_cond.loc[r.name, 'twii'], axis=1)

    def buy_logic(self, sid, date):
        return sid in self.selected[date]

    def sell_logic(self, sid, date, **kwargs):
        cond1 = kwargs['holding_days'] >= 126
        return any([cond1])
