import requests
from io import StringIO
import time
import pandas as pd
import os
import os.path as osp
import pickle as pkl
import datetime as dt
import numpy as np
from data.database.interface import execute_sql, search_table, res_to_df

cache_path = "./cache/"


# 要求一個資料的 dataframe
def get(item, before=None, c_index=None, no_sid=False, update=False):
    # 確認有個快取路徑存在
    if not osp.isdir(cache_path):
        os.mkdir(cache_path)
    path = cache_path + item + ".pkl"
    cache_update = False

    # 已有快取
    if osp.exists(path):
        df = pkl.load(open(path, 'rb'))

        if update:
            # 從快取最新開始往後找資料
            new_data = _get_data(item, str(df.index[-1] + dt.timedelta(days=1)))
            if len(new_data):
                df = df.append(new_data)
                cache_update = True
    # 沒快取，預設從 2010 年取資料
    else:
        df = _get_data(item, "2010-01-01")
        cache_update = True

    # 快取有更新
    if cache_update:
        df = df.sort_index()
        pkl.dump(df, open(path, 'wb'))

    # 如果少了 上市公司清單內有的代號 則補齊
    if not no_sid:
        df[pd.Index(twse).difference(df.columns)] = np.nan
        df = df[twse].ffill().truncate(before=before)

    if c_index is not None:
        df = _align_idx_with_ohlcv(c_index, df)

    df = df.dropna(axis=1, how='all')

    return df


def _get_data(item: str, n_or_date):
    # 找 db 中哪個 table 存有要求的資料
    schema_name = search_table(item)

    # 要求的是天數
    if isinstance(n_or_date, int):
        sql = 'get_n_days'
        params = (schema_name, n_or_date, item, schema_name)
    # 要求的是日期
    else:
        sql = 'get_from_date'
        params = (item, schema_name, n_or_date)
    g = res_to_df(*execute_sql(sql, params=params)).set_index("date").groupby("sid")
    df = pd.DataFrame({k: g.get_group(k)[item] for k in g.groups.keys()})

    return df


def get_adj_ratio(c_index, c_columns):
    df = res_to_df(*execute_sql("SELECT * FROM dividend")).set_index("date")
    ratio = df.groupby("sid").apply(lambda t: (t['after'] / t['before'])
                                    [::-1].cumprod()[::-1].shift(-1).fillna(1))
    r = pd.DataFrame({sid: ratio.loc[sid] for sid in ratio.index.droplevel(1)})
    r = _align_idx_with_ohlcv(c_index, r, back_fil=True)
    r[c_columns.difference(r.columns)] = 1.0
    r = r[c_columns]

    return r


def _align_idx_with_ohlcv(c_index, df, back_fil=False):
    """
    different data may have different index(datetime), so we need to unify them based on close price df index
    :param c_index:  close price dataframe index
    :param df: the df that need to align with close price df index
    :param back_fil: boolean, call df backfill or not
    :return: df with aligned index
    """
    df = df.reindex(index=c_index)
    # assert df.index.is_monotonic_increasing
    # for d in c_index.difference(df.index):
    #     df.loc[d] = [np.nan] * df.shape[1]

    df = df.ffill()
    if back_fil:
        df = df.backfill()
    # df = df.drop(df.index.difference(c_index))

    return df


# 獲取上市公司清單
def twse_list():
    res = None
    while True:
        try:
            res = requests.get('https://dts.twse.com.tw/opendata/t187ap03_L.csv')
            break
        except requests.exceptions.ConnectionError:
            print("fetch twse list, got connection error, try after 10 sec")
            time.sleep(10.0)
            continue
    res.encoding = 'utf-8'
    df = pd.read_csv(StringIO(res.text), index_col=['公司代號'])
    time.sleep(3.0)

    return list(map(str, list(df.index)))


twse = twse_list()
