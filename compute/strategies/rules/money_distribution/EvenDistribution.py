from strategies.rules.money_distribution.Base import MoneyDistribution

FEE = 1.425e-3 * 0.6
TAX = 3e-3


# if   you don't have cash on hand more than "max_price_for_one", then you cannot buy
# else you will buy the max possible shares of the stock (include tax & fee)
# note: this value will alter during process (based on current portfolio value)
class EvenDistribution(MoneyDistribution):
    def __init__(self, args, strategy_name: str, init_balance=1e3, div_const=10):
        super().__init__(args, strategy_name, init_balance)
        self.max_price_for_one = self.init_balance // div_const
        self.div_const = div_const

    def try_to_buy(self):
        recommendation = self.get_buy_recommendation()
        if recommendation is None:
            return
        # for each recommendation
        for row in recommendation.iterrows():
            open_price, sid, tid = row[1].open_price, row[1].sid, row[1].tid
            if sid not in self.c:
                continue
            if self.money > self.max_price_for_one > open_price * (1 + FEE):
                shares = self.max_price_for_one // (open_price * (1 + FEE))
                self.buy(tid, sid, open_price, shares)

    def try_to_sell(self):
        recommendation = self.get_sell_recommendation()
        if recommendation is None:
            return
        # for each recommendation
        for row in recommendation.iterrows():
            close_price, sid, tid = row[1].close_price, row[1].sid, row[1].tid
            self.sell(tid, sid, close_price, shares=self.get_shares(tid))

    def reaction_after_sell(self):
        cur_value = self.cal_value()
        self.max_price_for_one = cur_value // self.div_const
