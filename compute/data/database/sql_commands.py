sql_commands = {
    "get_trading_record": """
        SELECT * 
        FROM trading_record 
        WHERE close_date IS NULL AND strategy_name='{}'
    """,

    "get_holding": """
        SELECT * 
        FROM trading_record 
        WHERE open_date IS NOT NULL AND close_date IS NULL AND strategy_name='{}'
    """,

    "get_history_record": """
        SELECT * 
        FROM trading_record 
        WHERE open_date IS NOT NULL AND strategy_name='{}'
    """,

    "drop_history_record": """
        DELETE 
        FROM trading_record 
        WHERE strategy_name='{}'
    """,

    "add_trading_record": """
        INSERT INTO trading_record (sid, strategy_name, trader_code, holding_days, last_check)
        VALUES('{}', '{}', '{}', '{}', '{}')
        RETURNING tid
    """,

    "update_record_on_sell": """
        UPDATE trading_record 
        SET close_date='{}', close_price='{}',
            holding_days='{}', pnl='{}', 
            tax='{}', fee='{}' 
        WHERE tid={}
    """,

    "update_record_on_buy": """
        UPDATE trading_record 
        SET open_date='{}', open_price='{}',
            long_short='{}', shares='{}'
        WHERE tid={}
    """,

    "update_last_check": """
        UPDATE trading_record
        SET last_check='{}'
        WHERE tid={}
    """,

    "update_holding_days": """
        UPDATE trading_record 
        SET holding_days='{}'
        WHERE tid={}
    """,

    "update_pnl": """
        UPDATE trading_record 
        SET pnl='{}'
        WHERE tid={}
    """,

    "search_table": """
        select t.table_schema,
               t.table_name
        from information_schema.tables t 
        inner join information_schema.columns c on c.table_name = t.table_name
                                                and c.table_schema = t.table_schema
        where c.column_name = '{}'
            and t.table_schema not in ('information_schema', 'pg_catalog')
            and t.table_type = 'BASE TABLE'           
        order by t.table_schema;                                         
    """,

    "get_n_days": """
        WITH dts AS (
            select distinct date
            from {}
            order by date desc
            fetch first {} rows only)
        SELECT sid, date, {}
        FROM {}
        WHERE date IN (SELECT date FROM dts)
    """,

    "get_from_date": """
        SELECT sid, date, {}
        FROM {}
        WHERE date >= '{}'
    """,

    "get_max_tid": """
        SELECT MAX(tid)
        FROM trading_record
    """
}
