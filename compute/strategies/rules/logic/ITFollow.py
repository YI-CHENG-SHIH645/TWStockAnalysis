from strategies.rules.logic import Logic
from talib.abstract import MA
import pandas as pd


class ITFollowLogic(Logic):
    strategy_name = "ITFollow"
    trader_code = "001"
    mature_day = 25
    stop_loss = 0.06

    def _cal_indicators(self):
        it = self.get('investment_trust')
        issued_shares = self.get('issued_shares')
        twii_c = self.get('twii_close')
        twii_ma25 = twii_c[['twii']].apply(lambda c: MA(c, timeperiod=25))

        # 投信買超 200 張
        cond1 = it / 1e3 > 200

        # 公司市值小於 10 億
        cond2 = issued_shares * 10 < 1e9

        twii_cond = pd.DataFrame(~(
                (twii_c < twii_ma25) &
                (twii_ma25 < twii_ma25.shift(1))
        ))

        self.select = (cond1 & cond2).apply(lambda r: r & twii_cond.loc[r.name, 'twii'], axis=1)

    def buy_logic(self, sid, date):
        return sid in self.selected[date]

    def sell_logic(self, sid, date, **kwargs):
        cond1 = kwargs['holding_days'] >= 30
        return any([cond1])
