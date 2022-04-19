"""
Utility functions
"""
import json
import logging
import warnings

import pandas as pd
from unicorn_binance_rest_api import BinanceRestApiManager as RestManager

from jellyfish import PRIVATE_DATA_PATH, CACHE_PATH
from jellyfish.backtesting.stretegy import Strategy
from jellyfish.backtesting import Backtest


def _load_binance_credentials():
    """
    Loads json with Binance API credentials
    :return: json with creds
    """
    try:
        with (PRIVATE_DATA_PATH / 'binance_creds.json').open() as creds_file:
            return json.load(creds_file)

    except FileNotFoundError as exc:
        logging.warning(exc)
        return {
            'key': None,
            'secret': None
        }


def plot_ohlc(ohlc: pd.DataFrame, show_legend=False):
    """
    Plot OHLC chart from dataframe
    Args:
        show_legend: show equity/pnl legend
        ohlc: dataframe
    """
    backtest = Backtest(ohlc, strategy=Strategy, cash=10_000, commission=.002)
    backtest.run()
    plot_ohlc_from_backtest(backtest, show_legend=show_legend)


def plot_ohlc_from_backtest(backtest: Backtest, filepath=None, open_browser=True, show_legend=True):
    """
    Plots candlestick chart from dataframe
    @param backtest: backtesting engine
    @param filepath: file path
    @param open_browser: open browser
    @param show_legend: show equity/pnl legend
    """
    if filepath is None:
        filepath = (CACHE_PATH / 'test.html').as_posix()

    backtest.plot(filename=filepath, show_legend=show_legend, open_browser=open_browser)


def load_binance_client():
    """
    Loads Binance reset manager client
    :return: RestManager client
    """
    creds = _load_binance_credentials()
    return RestManager(creds['key'], creds['secret'])


def disable_warnings():
    """
    Disables all warnings
    """
    warnings.filterwarnings("ignore")


def last(sequence):
    """
    Get last element from the sequence
    Args:
        sequence: subscriptable sequence

    Returns: last element from the sequence
    """
    return list(sequence)[len(sequence)-1]


def first(sequence):
    """
    Get first element from the sequence
    Args:
        sequence: subscriptable sequence

    Returns: first element from the sequence
    """
    return list(sequence)[0]


def collapse_candle(data: pd.DataFrame, agg: dict):
    """
    Downsample OHLC candle
    Args:
        data: OHLC frame
        agg: aggregation dict

    Returns: frame with aggregated result
    """
    return [data[col].agg(func) for col, func in agg.items()]
