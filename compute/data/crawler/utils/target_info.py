from data.crawler.utils.data_preprocessing import ResponseTextToDataframe
from datetime import datetime


class TargetInfo:
    def __init__(self, url, schema_name, first_date, res_no_data_text_len, typ: str,
                 freq="D", start_end=False, no_sid=False):
        assert hasattr(ResponseTextToDataframe, schema_name)
        self.url = url
        self.schema_name = schema_name
        self.first_date = first_date
        self.res_no_data_text_len = res_no_data_text_len
        self.data_processing_func = getattr(ResponseTextToDataframe, schema_name)
        self.typ = typ
        self.freq = freq
        self.start_end = start_end
        self.no_sid = no_sid


target_url_mapping = {
    "價量資訊": TargetInfo(
        url="https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALLBUT0999",
        schema_name="ohlcv",
        first_date="20100101",
        res_no_data_text_len=0,
        typ="TWSE",
    ),
    "法人買賣": TargetInfo(
        url="https://www.twse.com.tw/fund/T86?response=csv&date={}&selectType=ALLBUT0999",
        schema_name="legal_person_buy_sell",
        first_date="20120501",
        res_no_data_text_len=2,
        typ="TWSE",
    ),
    "外資持股比": TargetInfo(
        url="https://www.twse.com.tw/fund/MI_QFIIS?response=csv&date={}&selectType=ALLBUT0999",
        schema_name="foreign_investor_holding",
        first_date="20100101",
        res_no_data_text_len=600,
        typ="TWSE",
    ),
    "本益比殖利率股價淨值比": TargetInfo(
        url="https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={}&selectType=ALL",
        schema_name="pepb",
        first_date="20100101",
        res_no_data_text_len=2,
        typ="TWSE",
    ),
    "資產負債表": TargetInfo(
        url="https://mops.twse.com.tw/mops/web/ajax_t163sb05",
        schema_name="balance_sheet",
        first_date="20130101",
        res_no_data_text_len=15000,
        typ="MOPS"
    ),
    "綜合損益表": TargetInfo(
        url="https://mops.twse.com.tw/mops/web/ajax_t163sb04",
        schema_name="income_statement",
        first_date="20130101",
        res_no_data_text_len=15000,
        typ="MOPS"
    ),
    "除權息結果": TargetInfo(
        url="https://www.twse.com.tw/exchangeReport/TWT49U?response=csv&strDate={}&endDate="
            + str(datetime.now().date()).replace("-", ""),
        schema_name="dividend",
        first_date="20100101",
        res_no_data_text_len=2,
        typ="TWSE",
        start_end=True
    ),
    "大盤指數": TargetInfo(
        url="https://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=csv&date={}",
        schema_name="twii",
        first_date="20100101",
        res_no_data_text_len=2,
        typ="TWSE",
        freq="MS",
        no_sid=True
    )
}
