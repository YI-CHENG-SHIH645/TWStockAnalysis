from data.utils import talib_format
import data
import datetime as dt
from collections import defaultdict
import pandas as pd


class Logic:
    strategy_name = None  # required
    trader_code = None  # required
    mature_day = 25  # required
    stop_loss = None  # required
    holding_days_th = -1  # required
    __data = None
    o = data.get('open')
    h = data.get('high')
    l = data.get('low')
    c = data.get('close')
    v = data.get('volume')
    adj_ratio = data.get_adj_ratio(c.index, c.columns)

    # cumtime: 28.9s
    # how to use this information?  check ./BBandsLogic.py for example
    # after understanding the data structure, you can start to build ur own strategies
    # ********* note: remember to inherit this base class "Logic" *********
    def __init__(self, start_date, cpp: bool, skip_select=False):
        Logic.__prepare_base_data()
        self.close_start = start_date - dt.timedelta(days=self.mature_day * 2)
        self.start_date = start_date
        self.cpp = cpp

        self.select, self.selected = None, None
        self._cal_indicators()
        if not skip_select:
            self.__make_selected_dict()

    @classmethod
    def __prepare_base_data(cls):
        if cls.__data is None:
            cls.__data = {
                "adj_o": cls.o * cls.adj_ratio,
                "adj_h": cls.h * cls.adj_ratio,
                "adj_l": cls.l * cls.adj_ratio,
                "adj_c": cls.c * cls.adj_ratio,
                "talib_dict": talib_format(cls.o,
                                           cls.h,
                                           cls.l,
                                           cls.c,
                                           cls.v)
            }

    def get(self, tgt: str, align=True):
        if tgt not in self.__data:
            self.__data[tgt] = self.__get_data(tgt, align=align)
        return self.__data[tgt]

    def __make_selected_dict(self):
        # assert self.select is not None
        # for date in self.select.index:
        #     selected = self.select.loc[date][self.select.loc[date]].index
        #     self.selected.update({date: selected})
        idx, col = self.select.values.nonzero()
        df = pd.DataFrame.from_records(zip(self.select.index[idx], self.select.columns[col]), columns=['date', 'sid'])
        if self.cpp:
            df['date'] = df['date'].astype(str)
            self.selected = defaultdict(set, (
                df
                .groupby('date', sort=False)
                ['sid']
                .apply(set)
                .to_dict()
            ))
        else:
            df['date'] = pd.to_datetime(df['date'])
            self.selected = defaultdict(set, (
                df
                .groupby('date', sort=False)
                ['sid']
                .apply(set)
                .to_dict()
            ))

    def __get_data(self, tgt: str, align=True):
        """
        :param tgt: what to load
        :param align: align index with close price index (ex: financial report)
        :return:
        """
        c = getattr(self, "c", None)
        return data.get(tgt,
                        before=self.close_start,
                        c_index=c.index if (c is not None and align) else None,
                        no_sid=('twii' in tgt))

    def _cal_indicators(self):
        raise NotImplementedError

    def buy_logic(self, sid, date):  # required
        raise NotImplementedError

    def sell_logic(self, sid, date, **kwargs):  # required
        raise NotImplementedError
