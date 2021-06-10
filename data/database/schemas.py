schemas = {
    "brokers": """
        CREATE TABLE IF NOT EXISTS brokers (
            broker VARCHAR(20) NOT NULL,
            stock_id VARCHAR(20) NOT NULL,
            buy integer NOT NULL,
            sell integer NOT NULL,
            weighted_avg_buy float NOT NULL,
            weighted_avg_sell float NOT NULL,
            date date NOT NULL,
            PRIMARY KEY(broker, stock_id, date)
        );
        """,
    "ohlcv": """
        CREATE TABLE IF NOT EXISTS ohlcv (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            volume integer,
            transaction integer,
            trade_value bigint,
            open float,
            high float,
            low float,
            close float,
            updn float,
            change float,
            last_best_bid_price float,
            last_best_bid_volume float,
            last_best_ask_price float,
            last_best_ask_volume float,
            pe float,
            date date,
            id VARCHAR(21) PRIMARY KEY
        );
        """,
    "legal_person_buy_sell": """
        CREATE TABLE IF NOT EXISTS legal_person_buy_sell (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            foreign_investor bigint,
            investment_trust bigint,
            dealer bigint,
            institutional_investor bigint,
            date date,
            id VARCHAR(21) PRIMARY KEY
        );
        """,
    "trading_record": """
        CREATE TABLE IF NOT EXISTS trading_record (
            tid bigserial PRIMARY KEY,
            sid VARCHAR(10),
            open_date date,
            open_price real,
            long_short VARCHAR(5),
            shares integer,
            close_date date,
            close_price real,
            holding_days integer,
            pnl real,
            tax real,
            fee real,
            strategy_name VARCHAR(30),
            trader_code VARCHAR(10),
            last_check date
        );
        """,
    "foreign_investor_holding": """
        CREATE TABLE IF NOT EXISTS foreign_investor_holding (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            issued_shares bigint,
            fi_holding_percentage float,
            date date,
            id VARCHAR(21) PRIMARY KEY
        );    
        """,
    "balance_sheet": """
        CREATE TABLE IF NOT EXISTS balance_sheet (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            total_equity bigint,
            date date,
            id VARCHAR(21) PRIMARY KEY
        );
        """,
    "income_statement": """
        CREATE TABLE IF NOT EXISTS income_statement (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            net_income bigint,
            date date,
            id VARCHAR(21) PRIMARY KEY
        );
        """,
    "pepb": """
        CREATE TABLE IF NOT EXISTS pepb (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            dy float,
            pe float,
            pb float,
            date date,
            id VARCHAR(21) PRIMARY KEY
        );
        """,
    "dividend": """
        CREATE TABLE IF NOT EXISTS dividend (
            sid VARCHAR(15) NOT NULL,
            sname VARCHAR(15) NOT NULL,
            before float,
            after float,
            date date,
            id VARCHAR(21) PRIMARY KEY
        )
    """,
    "twii": """
        CREATE TABLE IF NOT EXISTS twii (
            sid VARCHAR(15) NOT NULL,
            twii_open float,
            twii_high float,
            twii_low float,
            twii_close float,
            date date PRIMARY KEY
        )
    """
}
