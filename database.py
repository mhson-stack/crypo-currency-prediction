import os
from symtable import Symbol
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine
from apscheduler.schedulers.blocking import BlockingScheduler


load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
HOST = os.getenv("HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_coin_history(symbol, start=None):
    """
    Use BINANCE API to retrieve Crypto Currency data
    Return : Pandas Dataframe
    """
    client = Client(API_KEY, SECRET_KEY)
    klines = client.get_historical_klines(symbol=f"{symbol}USDT", interval=client.KLINE_INTERVAL_1HOUR, start_str=start, end_str="1 day ago UTC")
    cols = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "CloseTime", 
            "QuoteAssetVolume", "NumTrades", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]
    coin_df = pd.DataFrame(klines, columns=cols)
    coin_df[["Open", "High", "Low", "Close", "Volume",
            "QuoteAssetVolume", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]] = coin_df[["Open", "High", "Low", "Close", "Volume", 
            "QuoteAssetVolume", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]].astype("float")
    coin_df["OpenTime"] = [datetime.fromtimestamp(ts // 1000) for ts in coin_df["OpenTime"]]
    coin_df["CloseTime"] = [datetime.fromtimestamp(ts // 1000) for ts in coin_df["CloseTime"]]
    print(f"Retrived {symbol}")
    return coin_df


def import_to_db(symbol, df, method="replace"):
    conn_string = f"postgresql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
    db = create_engine(conn_string)
    db_conn = db.connect()
    df.to_sql(symbol, con=db_conn, if_exists=method, index=False)
    
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    conn.commit()
    db_conn.close()
    conn.close()
    print(f"Importing {symbol}")
    return True


def export_db(symbol):
    conn_string = f"postgresql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM \"public\".\"{symbol}\"")
    df = cur.fetchall()
    conn.commit()
    conn.close()
    cols = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "CloseTime", 
            "QuoteAssetVolume", "NumTrades", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]
    coin_df = pd.DataFrame(df, columns=cols)
    print(f"Exporting {symbol}")
    return coin_df
    

def get_price(symbol):
    client = Client(API_KEY, SECRET_KEY)
    return client.get_avg_price(symbol=symbol)


def main():
    def wrapper():
        symbols = ["BTC", "ETH", "ETC", "XRP", "BNB"]
        # start = "1 day ago UTC" 
        start = "1 Dec, 2017"
        for symbol in symbols:
            temp_df = get_coin_history(symbol, start)
            import_to_db(symbol, temp_df, method="replace")
    # scheduler = BlockingScheduler({'apscheduler.timezone':'Asia/seoul'})
    # scheduler.add_job(func=wrapper, trigger='cron', hour=0, minute=0)
    # scheduler.start()
    wrapper()


if __name__ == "__main__":
    main()
