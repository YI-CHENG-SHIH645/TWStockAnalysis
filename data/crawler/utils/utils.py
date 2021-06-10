from data.database.interface import df_to_fd
from datetime import datetime


def get_latest_date(cur, target_info):
    cur.execute("SELECT max(date) FROM {}".format(target_info.schema_name))
    latest_date = cur.fetchall()[0][0]
    if latest_date is None:
        return datetime.strptime(target_info.first_date, "%Y%m%d").date()
    return latest_date


def fast_store_to_db(conn, cur, df, schema_name):
    fd = df_to_fd(df.fillna('None'))
    cur.copy_from(fd, schema_name, sep=",", null='None')
    conn.commit()
