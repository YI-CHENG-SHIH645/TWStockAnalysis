from io import StringIO
from datetime import datetime
import pandas as pd


class ResponseTextToDataframe:
    @staticmethod
    def twse_common(df):
        df = df.dropna(how='all', axis=1).dropna(how='any')
        df[df.columns[2:]] = df.iloc[:, 2:].apply(lambda s: pd.to_numeric(s.astype(str)
                                                                          .str.replace(",", "", regex=False),
                                                                          errors='coerce'))
        df['證券代號'] = df['證券代號'].str.replace('=', '', regex=False).str.replace('"', '', regex=False)
        return df

    @staticmethod
    def ohlcv(res_text):
        buffer = StringIO(res_text)
        header = ["證券代號" in l for l in res_text.split("\n")].index(True) - 1
        df = pd.read_csv(buffer, header=header).dropna(how='all', axis=1)
        df[df.columns[2:]] = df.iloc[:, 2:].apply(lambda t: pd.to_numeric(t.astype(str)
                                                                          .str.replace(",", "", regex=False)
                                                                          .str.replace("+", "1", regex=False)
                                                                          .str.replace("-", "-1", regex=False),
                                                                          errors='coerce'))
        df['證券代號'] = df['證券代號'].str.replace('=', '', regex=False).str.replace('"', '', regex=False)
        return df

    @staticmethod
    def legal_person_buy_sell(res_text):
        cols_mapping = {
            "證券代號": "證券代號",
            "證券名稱": "證券名稱",
            "投信買賣超股數": "投信買賣超",
            "自營商買賣超股數": "自營商買賣超",
            "三大法人買賣超股數": "三大法人買賣超",
            "外陸資買賣超股數(不含外資自營商)": "外資買賣超"
        }
        buffer = StringIO(res_text)
        df = pd.read_csv(buffer, header=1).dropna(how='all', axis=1).dropna(how='any')
        if "外陸資買賣超股數(不含外資自營商)" not in df.columns:
            cols_mapping.update({"外資買賣超股數": cols_mapping.pop("外陸資買賣超股數(不含外資自營商)", "外資買賣超")})
        else:
            cols_mapping.update({"外陸資買賣超股數(不含外資自營商)": cols_mapping.pop("外資買賣超股數", "外資買賣超")})
        cols = list(cols_mapping.keys())
        cols = cols[:2] + cols[-1:] + cols[2:-1]
        df = df[cols].rename(cols_mapping, axis=1)

        return ResponseTextToDataframe.twse_common(df)

    @staticmethod
    def foreign_investor_holding(res_text):
        buffer = StringIO(res_text)
        df = pd.read_csv(buffer, header=1)
        df = df[["證券代號", "證券名稱", "發行股數", "全體外資及陸資持股比率"]]
        return ResponseTextToDataframe.twse_common(df)

    @staticmethod
    def pepb(res_text):
        buffer = StringIO(res_text)
        df = pd.read_csv(buffer, header=1)
        df = df[['證券代號', '證券名稱', '殖利率(%)', '本益比', '股價淨值比']]
        return ResponseTextToDataframe.twse_common(df)

    @staticmethod
    def balance_sheet(res_text):
        bs = pd.concat(pd.read_html(res_text)[1:], axis=0, sort=False)
        bs[bs.columns[2:]] = bs.iloc[:, 2:].apply(
            lambda s: pd.to_numeric(s, errors='coerce')).copy()
        possible_name = ['權益總額', '權益合計', '權益總計']
        tgt_name = list(set(possible_name).intersection(bs.columns))[0]
        bs = bs[['公司代號', '公司名稱', tgt_name]].copy()
        bs = bs[bs[tgt_name].notna()].astype({tgt_name: int})
        bs = bs.drop('待註銷股本股數（單位：股）', axis=1, errors='ignore')

        return bs

    @staticmethod
    def income_statement(res_text):
        bs = pd.concat(pd.read_html(res_text)[1:], axis=0, sort=False)
        bs[bs.columns[2:]] = bs.iloc[:, 2:].apply(
            lambda s: pd.to_numeric(s, errors='coerce')).copy()
        bs = bs[['公司代號', '公司名稱', '本期淨利（淨損）']].copy()
        bs = bs[bs['本期淨利（淨損）'].notna()].astype({'本期淨利（淨損）': int})
        bs = bs.drop('原始認列生物資產及農產品之利益（損失）', axis=1, errors='ignore')
        bs = bs.drop('生物資產當期公允價值減出售成本之變動利益（損失）', axis=1, errors='ignore')

        return bs

    @staticmethod
    def dividend(res_text):
        buffer = StringIO(res_text)
        df = pd.read_csv(buffer, header=1)\
               .dropna(how="all", axis=1).set_index("資料日期").dropna(how="all", axis=0)
        df.index = [datetime.strptime(str(int(d[:-7]) + 1911) + d[-7:], "%Y年%m月%d日").date() for d in df.index]
        df = df[df.columns[:4]].apply(
            lambda c: c.astype(str).str.replace(",", "", regex=False).str.replace("=", "", regex=False).str.replace("\"", "", regex=False))
        df = df.astype({'除權息前收盤價': float, '除權息參考價': float})
        df = df.reset_index().rename({"index": "date", "股票代號": "證券代號"}, axis=1)
        df = df[list(df.columns[1:]) + list(df.columns[:1])]

        return df

    @staticmethod
    def twii(res_text):
        buffer = StringIO(res_text)
        df = pd.read_csv(buffer, header=1).dropna(how="all", axis=1).set_index("日期")
        df.index = [datetime.strptime(str(int(d[:-6]) + 1911) + d[-6:], "%Y/%m/%d").date() for d in df.index]
        df = df.apply(lambda c: c.str.replace(",", "", regex=False)).apply(pd.to_numeric).reset_index()
        df['sid'] = "twii"
        df.columns = ['date', 'o', 'h', 'l', 'c', 'sid']
        df = df[list(df.columns[-1:]) + list(df.columns[1:-1]) + list(df.columns[:1])]

        return df
