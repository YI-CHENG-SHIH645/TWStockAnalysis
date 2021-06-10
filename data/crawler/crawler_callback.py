from pandas.errors import ParserError
import datetime as dt
import requests
import itertools
import time
import pandas as pd


class Crawler:
    def __init__(self, target_info):
        self.target_info = target_info
        self.url = None

    def get_dates(self, latest_date, today):
        raise NotImplementedError

    def get_res_text(self, date):
        raise NotImplementedError

    def prepare_for_db(self, response_text, date):
        raise NotImplementedError


# 證券交易所
class TWSE(Crawler):
    def __init__(self, target_info):
        super().__init__(target_info)

    @staticmethod
    def date_to_str(date, with_dash=True):
        return str(date.date()) if with_dash else str(date.date()).replace("-", "")

    def get_dates(self, latest_date, today, freq="D"):
        date_start_to_update = latest_date + dt.timedelta(days=1)
        if freq == "MS":
            date_start_to_update = date_start_to_update.replace(day=1)
        return pd.date_range(date_start_to_update, today, freq=freq)

    def get_res_text(self, date):
        self.url = self.target_info.url.format(self.date_to_str(date, with_dash=False))
        response_text = requests.post(self.url).text

        return response_text

    def prepare_for_db(self, response_text, date, **kwargs):
        while True:
            try:
                df = self.target_info.data_processing_func(response_text)
                break
            except (ValueError, ParserError):
                print("Unknown Error, try again in 5 sec")
                time.sleep(5.0)
                response_text = requests.post(self.url).text
        if kwargs['no_sid']:
            cols = df.columns
            return df.set_index('date').truncate(
                before=kwargs['latest_date'] + dt.timedelta(days=1)).reset_index().reindex(columns=cols)
        if kwargs['start_end']:
            df.loc[:, 'id'] = df.date.astype(str).copy() + "_" + df['證券代號']
        else:
            df.loc[:, 'date'] = date
            df.loc[:, 'id'] = self.date_to_str(date, with_dash=False) + "_" + df['證券代號']

        return df


# 公開資訊觀測站
class MOPS(Crawler):
    def __init__(self, target_info):
        super().__init__(target_info)
        self.form_data = {
            "encodeURIComponent": 1,
            "step": 1,
            "firstin": 1,
            "off": 1,
            "isQuery": "Y",
        }
        self.IFRSs_start_year = "2013"
        self.Q = ["01", "02", "03", "04"]
        self.Q_date = ['-03-31', '-06-30', '-09-30', '-12-31']
        self.url = None
        self.year, self.season = None, None

    @staticmethod
    def date_to_str(date):
        return "-".join([str(item) for item in date])

    def get_dates(self, latest_date, today, freq=None):
        years = list(range(int(self.IFRSs_start_year) if latest_date == ""
                           else latest_date.year, today.year+1))
        return [item for item in list(itertools.product(years, self.Q))
                if (str(item[0]) + self.Q_date[int(item[1]) - 1]) > str(latest_date)]

    def get_res_text(self, date):
        self.year, self.season = date
        self.url = self.target_info.url
        res = []
        for TYPE in ["sii", "otc"]:
            self.form_data.update({"year": self.year-1911, "season": int(self.season), "TYPEK": TYPE})
            res.append(requests.post(self.url, data=self.form_data).text)
            if TYPE == "sii":
                time.sleep(3.0)
        return res

    def prepare_for_db(self, response_text, date, **kwargs):
        df = self.target_info.data_processing_func(response_text)
        df.loc[:, 'date'] = str(self.year) + self.Q_date[int(self.season) - 1]
        df.loc[:, 'id'] = df['date'].iloc[0] + "_" + df['公司代號'].astype(str)

        return df
