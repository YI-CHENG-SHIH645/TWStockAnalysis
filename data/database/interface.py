from io import BytesIO, TextIOWrapper
import psycopg2
from data.database.config import psql_config
from data.database import schemas, sql_commands
import pandas as pd


class PsqlConnect:
    def __enter__(self):
        self.conn = psycopg2.connect(**psql_config)
        self.cur = self.conn.cursor()
        return self.conn, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()


def execute_sql(sql_command: str, params=(), cur=None, return_result=True):
    sql_command = sql_commands[sql_command].format(*params) if sql_command in sql_commands else sql_command
    # 不給 cur 則開一個新的連接
    if cur is None:
        with PsqlConnect() as (conn, cur):
            cur.execute(sql_command)
            conn.commit()
            if return_result:
                res = cur.fetchall()
                return res, cur.description
    else:
        cur.execute(sql_command)
        if return_result:
            res = cur.fetchall()
            return res, cur.description


def create_table(cur, table_name):
    assert table_name in schemas
    cur.execute(schemas[table_name])


def df_to_fd(df):
    """
    把 df 包成準備被 copy from 進 db 的形式
    :param df: dataframe
    :return: csv file format
    """
    output = BytesIO()
    wrapper = TextIOWrapper(
        output,
        encoding='utf-8',
        write_through=True,
        newline=''
    )
    _ = wrapper.write(df.to_csv(index=False, line_terminator='\n'))
    wrapper.seek(0)
    next(wrapper)
    return wrapper


def res_to_df(res, cur_des):
    return pd.DataFrame(res, columns=[cur_des[i][0] for i in range(len(cur_des))])


def search_table(col_name):
    """
    :param col_name: data you want to search
    :return: table name
    """
    res, _ = execute_sql('search_table', (col_name, ))

    return res[0][1]
