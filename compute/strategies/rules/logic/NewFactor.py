import numpy as np
from talib.abstract import MA
from strategies.rules.logic import Logic
from data.utils import date_to_latest_season, \
                       season_to_public_date, fill_after_pub_date, get_season
from datetime import datetime


class NewFactor(Logic):
    strategy_name = "NewFactor"
    trader_code = "001"
    mature_day = 130
    stop_loss = 0.06
    holding_days_th = 60

    def _cal_indicators(self):
        pb = self.get("pb")  # 股價淨值比
        net_income = self.get("net_income", align=False)  # 稅後淨利
        total_equity = self.get("total_equity", align=False)  # 權益總計
        self.ma20 = self.get('adj_c').apply(lambda c: MA(c, timeperiod=20))
        origin_idx = pb.index

        # 股東權益報酬率 = 稅後淨利 / 權益總計
        roe = (net_income / total_equity) * 100
        roe = roe.truncate(after=get_season(datetime.now().date()))

        # ROE成長 = 本季 ROE / 上季 ROE
        roe_fac = (roe / roe.shift(1)).dropna(how="all")
        # 還沒到最晚公佈日，但有些公司已經公布有值了，但pb會被歸類到上一季，所以沒辦法先算
        roe_fac = roe_fac.truncate(after=get_season(datetime.now().date()))

        # pb的時間序列轉換成最近一季的日期
        pb.index = date_to_latest_season(pb.index)

        # 依據ROE成長的最早時間，處理股價淨值比的時間序列(align)
        pb = pb.truncate(before=roe_fac.index.min())

        # 把pb的時間序列照最近一季的日期分組，再把對應季的ROE成長 除上 pb
        new_factor = pb.groupby(pb.index).apply(lambda t: 1 / t.div(roe_fac.loc[t.index[0]]))

        # 轉換為原始的時間序列(每日)
        new_factor.index = origin_idx[-len(new_factor):]
        new_factor = new_factor.dropna(how="all", axis=1)

        # 本季ROE>3 且 上季ROE>1
        roe_cond = ((roe > 3) & (roe.shift(1) > 1)).iloc[1:]

        # 複製一個格式和 new factor 一樣的 df
        roe_aligned = new_factor.copy()
        roe_aligned.loc[:, :] = np.nan

        # 給定一個季日期，找到其對應公布日
        pub_dates = season_to_public_date(roe_cond.index)

        # 再對應到(右移)最接近的每日日期上，從那天開始就可以看到這個季日期所計算出的資訊
        roe_aligned = fill_after_pub_date(roe_aligned, roe_cond, pub_dates)

        # 10天內有3個月創新高的收盤
        cond1 = (self.c.rolling(60).max() == self.c).rolling(10).sum() > 0
        # 本季ROE>3 且 上季ROE>1
        cond2 = roe_aligned
        # 價格高於7元 且 成交量高於100張
        cond3 = (self.c > 7) & (self.v > 100000)

        # 把有滿足上述條件的股票的 new factor 值填入
        res = (new_factor * (cond1 & cond2 & cond3).dropna(how="all", axis=1)).fillna(0)

        # 根據每天找出該值最大的前三個且該值要大於0(也就是ROE要有成長)
        self.select = res.apply(lambda t: t.nlargest(3), axis=1) > 0

    def buy_logic(self, sid, date):
        return sid in self.selected[date]

    def sell_logic(self, sid, date, **kwargs):
        cond1 = kwargs['holding_days'] >= self.holding_days_th
        if kwargs['holding_days'] % 11 == 0:
            cond1 = cond1 or self.get('adj_c').loc[date, sid] < self.ma20.loc[date, sid]

        return cond1
