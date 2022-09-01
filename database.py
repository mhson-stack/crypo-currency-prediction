import os
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine


load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
HOST = os.getenv("HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_coin_history(symbol, start=None, end=None):
    """
    Use BINANCE API to retrieve Crypto Currency data
    Return : Pandas Dataframe
    """
    client = Client(API_KEY, SECRET_KEY)
    klines = client.get_historical_klines(symbol=f"{symbol}USDT", 
        interval=client.KLINE_INTERVAL_1HOUR, 
        start_str=start, end_str=end)

    cols = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "CloseTime", 
            "QuoteAssetVolume", "NumTrades", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]
    coin_df = pd.DataFrame(klines, columns=cols)

    coin_df[["Open", "High", "Low", "Close", "Volume",
            "QuoteAssetVolume", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]] = coin_df[["Open", "High", "Low", "Close", "Volume", 
            "QuoteAssetVolume", "TakerBuyBaseAssetVolume", 
            "TakerBuyQuoteAssetVolume", "Ignore"]].astype("float")

    coin_df["OpenTime"] = [datetime.fromtimestamp((ts + 32400000) // 1000) for ts in coin_df["OpenTime"]]
    coin_df["CloseTime"] = [datetime.fromtimestamp((ts + 32400000) // 100) for ts in coin_df["CloseTime"]]
    print(f"Retrived {symbol}")
    return coin_df


def import_to_db(table_name, df, method="replace"):
    conn_string = f"postgresql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
    db = create_engine(conn_string)
    db_conn = db.connect()
    df.to_sql(table_name, con=db_conn, if_exists=method, index=False)
    
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    conn.commit()
    db_conn.close()
    conn.close()
    print(f"Imported {table_name}")
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
    pass

if __name__ == "__main__":
    main()
