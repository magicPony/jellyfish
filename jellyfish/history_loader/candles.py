import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache

import numpy as np
import pandas as pd
from unicorn_binance_rest_api.helpers import interval_to_milliseconds

from jellyfish.constants import (CANDLES_DB_PATH, OPEN, HIGH, LOW, CLOSE, VOLUME,
                                 QUOTE_ASSET_VOLUME, NUM_OF_TRADES, TAKER_BUY_ASSET_VOLUME,
                                 TAKER_SELL_ASSET_VOLUME)
from jellyfish.core import Client
from jellyfish.history_loader.orderbook import load_orderbook_history

CANDLES_IN_CHUNK = 1000

TIMESTAMP = 'Timestamp'


class ResponseDTypes(Enum):
    """
    SQLite data types
    """
    REAL = 'REAL'
    INT = 'INT'


RESPONSE_STRUCTURE = {
    OPEN: ResponseDTypes.REAL,
    HIGH: ResponseDTypes.REAL,
    LOW: ResponseDTypes.REAL,
    CLOSE: ResponseDTypes.REAL,
    VOLUME: ResponseDTypes.REAL,
    TIMESTAMP: ResponseDTypes.INT,
    QUOTE_ASSET_VOLUME: ResponseDTypes.REAL,
    NUM_OF_TRADES: ResponseDTypes.INT,
    TAKER_BUY_ASSET_VOLUME: ResponseDTypes.REAL,
    TAKER_SELL_ASSET_VOLUME: ResponseDTypes.REAL
}


def create_db_connection(table_name):
    """
    Parameters
    ----------
    table_name : db table name

    Returns
    -------
    Create candlestick cache database connection
    """
    connection = sqlite3.connect(CANDLES_DB_PATH.as_posix())
    cursor = connection.cursor()
    cmd = f'CREATE TABLE IF NOT EXISTS {table_name} ' \
          f'({",".join(f"{k} {v.value}" for k, v in RESPONSE_STRUCTURE.items())},' \
          f'PRIMARY KEY({TIMESTAMP}))'
    cursor.execute(cmd)

    return connection


def clean_candles_cache():
    """
    Clear candles cache
    """
    connection = sqlite3.connect(CANDLES_DB_PATH.as_posix())
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    available_tables = [t[0] for t in cursor.fetchall()]
    for table_name in available_tables:
        cursor.execute(f'DELETE FROM {table_name}')

    connection.commit()


def get_sample_frame(max_records=1000):
    """
    Parameters
    ----------
    max_records : limit of records to load

    Returns
    -------
    Get some sample frame (mainly in debug purposes)
    """
    connection = sqlite3.connect(CANDLES_DB_PATH.as_posix())
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    available_tables = [t[0] for t in cursor.fetchall()]
    for table_name in available_tables:
        cursor.execute(f'SELECT * FROM {table_name} LIMIT {max_records}')
        raw_candles = cursor.fetchall()
        if len(raw_candles) > 0:
            return parse_raw_candles(raw_candles)

    return None


def parse_raw_candles(raw_candles):
    """
    Parameters
    ----------
    raw_candles : japanese candlestick plain raw data

    Returns
    -------
    dataframe with candlesticks
    """
    raw_candles = np.array(raw_candles)
    frame = pd.DataFrame()
    for i, (col_name, val_type) in enumerate(RESPONSE_STRUCTURE.items()):
        frame[col_name] = raw_candles[:, i].astype(
            np.int if val_type == ResponseDTypes.INT else np.float)

    frame['Date'] = pd.to_datetime(frame.Timestamp * 1e6)
    frame.drop(TIMESTAMP.capitalize(), axis=1, inplace=True)
    frame.set_index('Date', inplace=True)
    return frame


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
    """
    Parameters
    ----------
    pair_sym : trading pair
    start_dt : start datetime
    end_dt : end datetime
    interval : candle sampling size
    client : Binance REST Client
    candles_num : number of candles to load
    read_orderbook : read alongside orderbook data

    Returns
    -------
    Get japanese candlestick chart from Binance
    """
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

    cmd = f'SELECT * FROM {table_name} ' \
          f'WHERE {start_dt.microsecond}<={TIMESTAMP} AND {TIMESTAMP}<={end_dt.microsecond}'
    cursor.execute(cmd)
    raw_candles = cursor.fetchall()
    if len(raw_candles) != candles_num:
        client = client or Client()

        binance_response = client.get_historical_klines(pair_sym, interval,
                                                        str(start_dt), str(end_dt))
        raw_candles = [candle[1:11] for candle in binance_response]

        cmd = f'INSERT OR IGNORE INTO {table_name} ' \
              f'VALUES ({",".join("?" for _ in range(np.shape(raw_candles)[1]))})'
        cursor.executemany(cmd, raw_candles)
        connection.commit()

    frame = parse_raw_candles(raw_candles)
    if read_orderbook:
        orderbook = load_orderbook_history(pair_sym, frame.index,
                                           max_lag=timedelta(milliseconds=interval_ms))
        frame = frame.join(orderbook)

    return frame
