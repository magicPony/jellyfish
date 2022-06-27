"""
Candles history manager module that is responsive for candles downloading/saving/loading from cache
"""
import logging
import math
from datetime import datetime, timedelta
from typing import Union

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from unicorn_binance_rest_api.helpers import interval_to_milliseconds

from jellyfish.constants import (CANDLES_HISTORY_PATH, DATE, OPEN, HIGH, LOW, CLOSE, VOLUME,
                                 QUOTE_ASSET_VOLUME, NUM_OF_TRADES, TAKER_BUY_ASSET_VOLUME,
                                 TAKER_SELL_ASSET_VOLUME)
from jellyfish.core import Client
from jellyfish.history_loader.orderbook import load_orderbook_history

CANDLES_IN_CHUNK = 1000


def clean_candles_cache():
    """
    Cleans candles cache data
    """
    CANDLES_HISTORY_PATH.mkdir(exist_ok=True, parents=True)
    for cached_file_path in CANDLES_HISTORY_PATH.iterdir():
        cached_file_path.unlink()


def binance_response_to_dataframe(candles) -> pd.DataFrame:
    """
    Transform binance response to dataframe
    :param candles: candles sequence
    :return: candles dataframe
    """

    def to_numbers(seq: list):
        return [int(i) if isinstance(i, int) else float(i) for i in seq]

    def to_datetime(timestamp):
        return datetime.fromtimestamp(timestamp // 1e3).strftime('%Y-%m-%d %H:%M')

    candles = [to_numbers(i) for i in candles]
    candles = np.array(candles)
    candles = pd.DataFrame({
        DATE: candles[:, 6],
        OPEN: candles[:, 1],
        HIGH: candles[:, 2],
        LOW: candles[:, 3],
        CLOSE: candles[:, 4],
        VOLUME: candles[:, 5],
        QUOTE_ASSET_VOLUME: candles[:, 7],
        NUM_OF_TRADES: candles[:, 8],
        TAKER_BUY_ASSET_VOLUME: candles[:, 9],
        TAKER_SELL_ASSET_VOLUME: candles[:, 10],
    })

    candles.Date = candles.Date.apply(to_datetime)
    candles.Date = pd.to_datetime(candles.Date)
    candles.set_index('Date', inplace=True)

    return candles


def read_candles_frame(frame_path):
    """
    Read dataframe with candles
    """
    frame = pd.read_csv(frame_path, index_col='Date', parse_dates=True, infer_datetime_format=True)
    frame.index.names = ['Date']
    return frame


def get_sample_frame():
    """
    Get random candles dataframe from cache if possible
    """
    CANDLES_HISTORY_PATH.mkdir(exist_ok=True, parents=True)
    for sample_path in CANDLES_HISTORY_PATH.iterdir():
        return read_candles_frame(sample_path)

    return None


def _load_candles_chunk(
        client: Union[None, Client],
        pair_sym: str,
        start_dt: datetime,
        end_dt: datetime,
        interval: str) -> pd.DataFrame:
    """
    Loads single chunk of candles history
    :param client: RestManager Binance client
    :param pair_sym: trading pair
    :param start_dt: start date
    :param end_dt: end date
    :param interval: candle interval
    :return: candles history chunk dataframe
    """
    cache_path = CANDLES_HISTORY_PATH / f'{pair_sym}_{interval}_{start_dt}_{end_dt}.csv'
    if cache_path.exists():
        logging.debug('Loading candles history from cache')
        return read_candles_frame(cache_path)

    logging.debug('Downloading candles history from Binance')
    candles = client.get_historical_klines(pair_sym, interval, str(start_dt), str(end_dt))
    frame = binance_response_to_dataframe(candles)
    cache_path.parent.mkdir(exist_ok=True, parents=True)
    frame.to_csv(cache_path)
    return frame


def load_candles_history(
        pair_sym: str,
        start_dt: datetime = None,
        end_dt: datetime = None,
        interval: str = '1h',
        *,
        client: Client = None,
        candles_num=None,
        read_orderbook=False) -> pd.DataFrame:
    """
    Downloads japanese candles from binance with cached data usage if possible
    :param pair_sym: trading pair
    :param start_dt: start date
    :param end_dt: end date
    :param interval: candle interval
    :param client: binance client
    :param candles_num: define number of candles to load
    :param read_orderbook: read orderbook data flag
    :return: candles dataframe
    """
    client = client or Client()
    assert start_dt is not None or end_dt is not None
    if candles_num is not None:
        duration = timedelta(milliseconds=interval_to_milliseconds(interval) * candles_num)
        if start_dt is not None:
            end_dt = start_dt + duration
        else:
            start_dt = end_dt - duration

    interval_ms = interval_to_milliseconds(interval)
    total_candles = (end_dt - start_dt) / timedelta(milliseconds=interval_ms)
    chunks_num = math.ceil(total_candles / CANDLES_IN_CHUNK)
    dates = [(start_dt + timedelta(milliseconds=i * interval_ms * CANDLES_IN_CHUNK))
             for i in range(chunks_num)] + [end_dt]

    result = []
    for chunk_start_dt, chunk_end_dt in tqdm(list(zip(dates[:-1], dates[1:]))):
        candles = _load_candles_chunk(client, pair_sym.upper(), chunk_start_dt, chunk_end_dt,
                                      interval)
        result.append(candles)

    result = pd.concat(result).sort_index().sort_index(axis=1)
    if read_orderbook:
        orderbook = load_orderbook_history(pair_sym, result.index,
                                           max_lag=timedelta(milliseconds=interval_ms))
        result = result.join(orderbook)

    result.index.name = DATE
    return result