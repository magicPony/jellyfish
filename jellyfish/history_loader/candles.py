import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache

import numpy as np
import pandas as pd
from unicorn_binance_rest_api.helpers import interval_to_milliseconds

from jellyfish.constants import CANDLES_DB_PATH
from jellyfish.core import Client
from jellyfish.history_loader.orderbook import load_orderbook_history

CANDLES_IN_CHUNK = 1000

TIMESTAMP = 'timestamp'


class ResponseDTypes(Enum):
    REAL = 'REAL'
    INT = 'INT'


RESPONSE_STRUCTURE = {
    'open': ResponseDTypes.REAL,
    'high': ResponseDTypes.REAL,
    'low': ResponseDTypes.REAL,
    'close': ResponseDTypes.REAL,
    'volume': ResponseDTypes.REAL,
    TIMESTAMP: ResponseDTypes.INT,
    'quote_asset_volume': ResponseDTypes.REAL,
    'num_of_trades': ResponseDTypes.INT,
    'taker_buy_asset_volume': ResponseDTypes.REAL,
    'taker_sell_asset_volume': ResponseDTypes.REAL
}


def load_from_db(cursor: sqlite3.Cursor,
                 table_name,
                 start_dt: datetime,
                 end_dt: datetime):
    cmd = f'SELECT * FROM {table_name} WHERE {start_dt.microsecond}<={TIMESTAMP} AND {TIMESTAMP}<={end_dt.microsecond}'
    cursor.execute(cmd)
    return cursor.fetchall()


def insert_to_db(cursor: sqlite3.Cursor,
                 table_name,
                 candles):
    cmd = f'INSERT OR IGNORE INTO {table_name} ' \
          f'VALUES ({",".join("?" for _ in range(np.shape(candles)[1]))})'
    cursor.executemany(cmd, candles)


def create_db_connection(table_name):
    connection = sqlite3.connect(CANDLES_DB_PATH.as_posix())
    cursor = connection.cursor()
    cmd = f'CREATE TABLE IF NOT EXISTS {table_name} ' \
          f'({",".join(f"{k} {v.value}" for k, v in RESPONSE_STRUCTURE.items())},' \
          f'PRIMARY KEY({TIMESTAMP}))'
    cursor.execute(cmd)

    return connection


def clean_candles_cache():
    CANDLES_DB_PATH.unlink(missing_ok=True)


def get_sample_frame(max_records=1000):
    try:
        connection = sqlite3.connect(CANDLES_DB_PATH.as_posix())
    except sqlite3.OperationalError:
        return None

    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    available_tables = [t[0] for t in cursor.fetchall()]
    for table_name in available_tables:
        cursor.execute(f'SELECT * FROM {table_name} LIMIT {max_records}')
        candles = cursor.fetchall()
        if len(candles) > 0:
            return parse_raw_candles(candles)

    return None


def parse_raw_candles(candles):
    candles = np.array(candles)
    df = pd.DataFrame()
    for i, (key, val_type) in enumerate(RESPONSE_STRUCTURE.items()):
        col_name = ''.join(word.capitalize() for word in key.split('_'))
        df[col_name] = candles[:, i].astype(np.int if val_type == ResponseDTypes.INT else np.float)

    df['Date'] = pd.to_datetime(df.Timestamp * 1e6)
    df.drop(TIMESTAMP.capitalize(), axis=1, inplace=True)
    df.set_index('Date', inplace=True)
    return df


@lru_cache(maxsize=20)
def load_candles_history(
        pair_sym: str,
        start_dt: datetime = None,
        end_dt: datetime = None,
        interval: str = '1h',
        *,
        client: Client = None,
        candles_num=None,
        read_orderbook=False):
    assert start_dt is not None or end_dt is not None
    interval_ms = interval_to_milliseconds(interval)
    if candles_num is not None:
        duration = timedelta(milliseconds=interval_to_milliseconds(interval) * candles_num)
        if start_dt is not None:
            end_dt = start_dt + duration
        else:
            start_dt = end_dt - duration

    else:
        candles_num = (end_dt - start_dt) // timedelta(milliseconds=interval_ms)

    table_name = pair_sym + interval
    connection = create_db_connection(table_name)
    cursor = connection.cursor()

    candles = load_from_db(cursor, table_name, start_dt, end_dt)
    if len(candles) != candles_num:
        client = client or Client()

        binance_response = client.get_historical_klines(pair_sym, interval, str(start_dt), str(end_dt))
        candles = [candle[1:11] for candle in binance_response]

        insert_to_db(cursor, table_name, candles)
        connection.commit()

    df = parse_raw_candles(candles)
    if read_orderbook:
        orderbook = load_orderbook_history(pair_sym, df.index, max_lag=timedelta(milliseconds=interval_ms))
        df = df.join(orderbook)

    return df
