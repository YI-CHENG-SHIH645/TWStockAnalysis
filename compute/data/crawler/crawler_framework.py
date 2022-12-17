from datetime import datetime
import time
from data.database.interface import create_table, PsqlConnect
from data.crawler import crawler_callback
from data.crawler.utils.target_info import target_url_mapping
from data.crawler.utils.utils import get_latest_date, fast_store_to_db
from requests.exceptions import ConnectionError


def crawler(target: str):
    assert target in target_url_mapping
    target_info = target_url_mapping[target]
    tgt_instance = getattr(crawler_callback, target_info.typ)(target_info)
    with PsqlConnect() as (conn, cur):
        create_table(cur, target_info.schema_name)
        latest_date = get_latest_date(cur, target_info)
        today = datetime.now()

        for date in tgt_instance.get_dates(latest_date, today, freq=target_info.freq):
            while True:
                try:
                    response_text = tgt_instance.get_res_text(date)
                    break
                except ConnectionError:
                    print("connection error, try again after 10 sec")
                    time.sleep(10.0)
                    continue
            response_text = [response_text] if isinstance(response_text, str) else list(response_text)

            for response_txt in response_text:
                if len(response_txt) > target_info.res_no_data_text_len:
                    df = tgt_instance.prepare_for_db(response_txt, date,
                                                     start_end=target_info.start_end,
                                                     no_sid=target_info.no_sid,
                                                     latest_date=latest_date)
                    fast_store_to_db(conn, cur, df, target_info.schema_name)
                    print(target_info.schema_name, tgt_instance.date_to_str(date), "updated")
                else:
                    print(target_info.schema_name, tgt_instance.date_to_str(date), "no data")
            time.sleep(3.0)
            if target_info.start_end:
                break
        print(target_info.schema_name, "is up to date", "#" + str(today.date()))
    print("\n", "-" * 60, "\n")
