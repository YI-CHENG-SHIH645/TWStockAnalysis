from strategies.rules.logic import Logic


class BBandsLogic(Logic):
    strategy_name = "BBANDS"
    trader_code = "001"
    mature_day = 25
    stop_loss = 0.06

    def _cal_indicators(self):
        from talib.abstract import BBANDS
        self.upper, self.ma20, self.lower = [self.c.copy(), self.c.copy(), self.c.copy()]
        for sid in self.c:
            self.upper.loc[:, sid], self.ma20.loc[:, sid], \
                self.lower.loc[:, sid] = BBANDS(self.talib_dict[sid], timeperiod=20, nbdevup=2.1)

        # 紅K 且 收盤站上布林上通道
        cond1 = (self.c > self.upper) & (self.c > self.o)
        # 今天成交量 大於 前五日均量兩倍
        cond2 = (self.v > 2 * self.v.rolling(5).mean())
        # 只買高於 15 元的股票
        cond3 = (self.c > 15)
        # 今天收盤價為 20日新高
        cond4 = (self.c == self.c.rolling(20).max())
        # 成交額高於 1千萬
        cond5 = (self.v * self.c > 1e7)

        self.select = cond1 & cond2 & cond3 & cond4 & cond5

    def buy_logic(self, sid, date):
        if self.cond_twii.loc[date].item():
            return False
        return sid in self.selected[date]

    # kwargs: open_price(停損), holding_days
    def sell_logic(self, sid, date, **kwargs):
        if self.cond_twii.loc[date].item():
            return True
        cond1 = kwargs['holding_days'] >= 30
        cond2 = self.c.loc[date, sid] < self.ma20.loc[date, sid]
        return any([cond1, cond2])
