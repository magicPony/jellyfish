import sqlite3
from enum import Enum
from datetime import datetime, timedelta
from functools import lru_cache

import numpy as np
from unicorn_binance_rest_api.helpers import interval_to_milliseconds

from jellyfish.constants import CANDLES_DB_PATH
from jellyfish.core import Client

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
                 end_dt: datetime,
                 interval_ms: int):
    microseconds_in_millisecond = timedelta(milliseconds=1) / timedelta(microseconds=1)

    first_timestamp = start_dt.timestamp() * microseconds_in_millisecond
    first_timestamp = first_timestamp + (interval_ms - first_timestamp % interval_ms) % interval_ms
    last_timestamp = end_dt.timestamp() * microseconds_in_millisecond

    cmd = f'SELECT * FROM {table_name} WHERE {first_timestamp}<={TIMESTAMP} AND {TIMESTAMP}<={last_timestamp}'
    return list(cursor.execute(cmd))


def insert_to_db(cursor: sqlite3.Cursor,
                 table_name,
                 candles: list[list]):
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

    candles = load_from_db(cursor, table_name, start_dt, end_dt, interval_ms)
    if len(candles) < candles_num - 3:  # (\/)(*--*)(\/)
        client = client or Client()

        binance_response = client.get_historical_klines(pair_sym, interval, str(start_dt), str(end_dt))
        candles = [candle[1:11] for candle in binance_response]

        insert_to_db(cursor, table_name, candles)
        connection.commit()

    candles = np.array(candles)
