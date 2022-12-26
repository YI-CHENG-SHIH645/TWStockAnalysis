from strategies.rules.logic import Logic
from talib.abstract import MA
import pandas as pd


class PEPBLogic(Logic):
    strategy_name = "PEPB"
    trader_code = "001"
    mature_day = 25
    stop_loss = 0.06

    def _cal_indicators(self):
        pe = self.get("pe")
        pb = self.get("pb")
        twii_c = self.get("twii_close")
        twii_ma25 = twii_c[['twii']].apply(lambda c: MA(c, timeperiod=25))

        # 本益比 小於 13
        cond1 = pe < 13

        # 股價淨值比 小於 0.7
        cond2 = pb < 0.7

        twii_cond = pd.DataFrame(~(
                (twii_c < twii_ma25) &
                (twii_ma25 < twii_ma25.shift(1))
        ))

        self.select = (cond1 & cond2).apply(lambda r: r & twii_cond.loc[r.name, 'twii'], axis=1)

    def buy_logic(self, sid, date):
        return sid in self.selected[date]

    def sell_logic(self, sid, date, **kwargs):
        cond1 = kwargs['holding_days'] >= 126
        return any([cond1])
