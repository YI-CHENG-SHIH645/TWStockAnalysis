import data
import bisect
import numpy as np
import datetime as dt
from datetime import datetime


# 財報公布日
public_date = ["03-31", "05-15", "08-14", "11-14"]

# 季日期
season_date = ["03-31", "06-30", "09-30", "12-31"]


# 檢查今天是不是交易日(透過資料庫的價量資訊今天有沒有被更新來決定)
def today_is_trading_day(today):
    latest_date = data.get("close").index[-1]
    if latest_date == today:
        return True
    return False


# 計算技術指標的格式
def talib_format(o, h, l, c, v):
    dic = {}
    for sid in c:
        dic[sid] = {"open": o[sid], "high": h[sid], "low": l[sid], "close": c[sid], "volume": v[sid]}
    return dic


# 以下為協調 財報日期 和 daily日期 的 utility functions

def date_to_latest_season(time_series):
    season_dates = []
    for d in time_series:
        season_dates.append(get_season(d))
    return season_dates


def season_to_public_date(time_series):
    return [datetime.strptime(str(d.year + 1 if str(d)[5:] == "12-31" else d.year) + "-" + public_date[
            (season_date.index(str(d)[5:]) + 1) % 4], "%Y-%m-%d").date() for d in time_series]


def fill_after_pub_date(df_filled, data_df, pub_dates):
    idx = np.searchsorted(df_filled.index.values, np.array(pub_dates))
    shifted_dates = df_filled.index[idx]
    df_filled.loc[shifted_dates, data_df.columns] = data_df.values
    # for idx, date in enumerate(pub_dates):
    #     shifted_date = df_filled.index[df_filled.index.get_loc(date, method='nearest')]
    #     while shifted_date not in df_filled.index:
    #         shifted_date += dt.timedelta(days=1)
    #     df_filled.loc[shifted_date, data_df.columns] = data_df.iloc[idx].values
    df = df_filled.ffill()

    return df


def get_season(date):
    year = date.year - 1 if str(date)[5:] <= "05-15" else date.year
    date = str(date)[5:]
    season_idx = (bisect.bisect_left(public_date, date) - 2) % len(public_date)

    return datetime.strptime(str(year) + "-" + season_date[season_idx], "%Y-%m-%d").date()
