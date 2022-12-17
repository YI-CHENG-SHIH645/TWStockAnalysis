import time
import requests
from io import StringIO
import pandas as pd
from datetime import datetime
from data.database.interface import df_to_fd, PsqlConnect, create_table
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings
import numpy as np
from data.utils import today_is_trading_day
from data.get import twse_list

disable_warnings(InsecureRequestWarning)
TODAY = datetime.now().date()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0.1) Gecko/2010010'
                  '1 Firefox/4.0.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
}


def _get_data(rs, stock_id, viewstate, eventvalidation):
    payload = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'RadioButton_Normal': 'RadioButton_Normal',
        'TextBox_Stkno': stock_id,
        'CaptchaControl1 ': 'Z67YB',
        'btnOK': '%E6%9F%A5%E8%A9%A2',
    }

    rs.post("https://bsr.twse.com.tw/bshtm/bsMenu.aspx", data=payload,
            headers=headers)  # , verify = False, stream = True )
    time.sleep(1)
    res = rs.get('https://bsr.twse.com.tw/bshtm/bsContent.aspx')
    return res


def _get_verify_code(rs):
    res = rs.get('https://bsr.twse.com.tw/bshtm/bsMenu.aspx', stream=True, verify=False, headers=headers, timeout=None)
    # ---------------
    # 從網頁中抓取一些關鍵字
    # ---------------
    import re

    # get view state
    view_state = re.search('VIEWSTATE"\\s+value=.*=', res.text)
    view_state = view_state.group()[18:]

    # get event_validation
    event_validation = re.search('EVENTVALIDATION"\\s+value=.*\\w', res.text)
    event_validation = event_validation.group()[24:]

    return view_state, event_validation


def _download_stock(stock_id):
    rs = requests.Session()
    view_state, event_validation = None, None

    # 不斷嘗試直到拿到 view_state 和 event_validation 為止
    while True:
        try:
            view_state, event_validation = _get_verify_code(rs)
            break  # 抓資料成功,進行下一步
        except Exception as e:
            print(e)  # 印出無法連線原因
            print('無法拿到資料, 等 31 sec')  # server好像會擋30sec
            time.sleep(31)
            continue  # 抓資料失敗,重新抓資料
    time.sleep(2)

    # 用 view_state 和 event_validation 組成 data 後， post 繞過驗證，再用 get 取得網頁資料
    res = _get_data(rs, stock_id, view_state, event_validation)
    res.encoding = 'big5'

    return res


def get_df(stock_id):
    fail_counts = 0

    # 有的時候會明明有資料卻拿不到的情況
    # 所以若看了沒資料就試到10次為止才放棄
    while True:
        if fail_counts == 10:
            print(stock_id, "no data")
            return None
        response = _download_stock(stock_id)
        if len(response.text) > 0:
            break
        else:
            fail_counts += 1
        print(stock_id, "response text 0, try again after 12 sec")
        time.sleep(12)

    # 成功拿到有內容的 response，處理成 dataframe
    lines = StringIO(response.text)
    lines = [line for line in lines if len(line.split(',')) == 11]
    df = pd.read_csv(StringIO('\n'.join(lines)))

    # 整理 dataframe
    first_df = df[df.columns[:5]]
    second_df = df[df.columns[6:]]
    second_df.columns = second_df.columns.str.replace('.1', '')
    final_df = first_df.append(second_df).set_index('序號').sort_index().dropna()
    final_df['stock_id'] = stock_id
    final_df['date'] = TODAY
    final_df = final_df.astype({'價格': 'float32', '買進股數': 'int32', '賣出股數': 'int32'})
    return final_df


def weighted_sum(x, weights):
    try:
        return np.average(x, weights=weights)
    except ZeroDivisionError:
        return 0.0


def _cal(df):
    return df.groupby(["券商", "stock_id"]).agg(
        buy=("買進股數", sum),
        sell=("賣出股數", sum),
        weighted_avg_buy=("價格", lambda x: weighted_sum(x, df.loc[x.index, "買進股數"])),
        weighted_avg_sell=("價格", lambda x: weighted_sum(x, df.loc[x.index, "賣出股數"]))
    ).reset_index()


def db_update_brokers():
    print(TODAY)

    # 確認今天是不是交易日
    if not today_is_trading_day(TODAY):
        print("today is not trading day, pass.")
        return

    # 取得上市公司清單
    stock_id_list = twse_list()
    table_name = 'brokers'
    with PsqlConnect() as (conn, cur):
        create_table(cur, table_name)
        for stock_id in stock_id_list:
            print(stock_id, end=" ")

            while True:
                try:
                    df = get_df(stock_id)
                    break
                except requests.exceptions.ConnectionError:
                    print("connection error, try after 1 minute")
                    time.sleep(60.0)
                    continue
            # 試了10次都拿不到資料(回傳為空)
            if df is None:
                continue

            df = _cal(df)
            df['date'] = TODAY
            anonymous_f = df_to_fd(df.fillna("None"))
            cur.copy_from(anonymous_f, table_name, sep=',', null='None')
            conn.commit()
            print("successfully update")
            time.sleep(12)
    print(TODAY)
    print("\n\n")


if __name__ == '__main__':
    db_update_brokers()
