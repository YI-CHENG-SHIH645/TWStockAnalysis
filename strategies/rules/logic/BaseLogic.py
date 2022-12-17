from data.utils import talib_format
import data
import datetime as dt


class Logic:
    strategy_name = None  # required
    trader_code = None  # required
    mature_day = 25  # required
    stop_loss = None  # required

    def __init__(self, start_date, skip_select=False):
        self.close_start = start_date - dt.timedelta(days=self.mature_day * 2)
        self.start_date = start_date
        # how to use this information?  check ./BBandsLogic.py for example
        # after understanding the data structure, you can start to build ur own strategies
        # ********* note: remember to inherit this base class "Logic" *********

        # 把價量讀進來  並且準備好計算技術指標的 dictionary
        self.o = self.get_data("open")
        self.h = self.get_data("high")
        self.l = self.get_data("low")
        self.v = self.get_data("volume")
        self.c = self.get_data("close")
        self.talib_dict = talib_format(*[getattr(self, attr) for attr in "ohlcv"])

        # 取得調整版本的 ohlc
        adj_ratio = data.get_adj_ratio(self.c.index, self.c.columns)
        self.adjo = self.o * adj_ratio
        self.adjh = self.h * adj_ratio
        self.adjl = self.l * adj_ratio
        self.adjc = self.c * adj_ratio
        self.adj_talib_dict = talib_format(self.adjo, self.adjh, self.adjl, self.adjc, self.v)

        self.select, self.selected = None, {}
        self._load_data()
        self._cal_indicators()
        if not skip_select:
            self._make_selected_dict()

    def _make_selected_dict(self):
        assert self.select is not None
        for date in self.select.index:
            selected = self.select.loc[date][self.select.loc[date]].index
            self.selected.update({date: selected})

    def get_data(self, tgt: str, align=True, no_sid=False):
        """
        :param tgt: what to load
        :param align: align index with close price index (ex: financial report)
        :param no_sid: do not add twse list sid (ex: twii)
        :return:
        """
        c = getattr(self, "c", None)
        return data.get(tgt,
                        before=self.close_start,
                        c_index=c.index if (c is not None and align) else None,
                        no_sid=no_sid)

    def _load_data(self):
        raise NotImplementedError

    def _cal_indicators(self):
        raise NotImplementedError

    def buy_logic(self, sid, date):  # required
        raise NotImplementedError

    def sell_logic(self, sid, date, **kwargs):  # required
        raise NotImplementedError
