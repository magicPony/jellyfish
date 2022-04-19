"""
Utility functions
"""
import json
import logging
import warnings

import pandas as pd
from unicorn_binance_rest_api import BinanceRestApiManager as RestManager

from jellyfish import PRIVATE_DATA_PATH
from jellyfish.core import Strategy, Backtest


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


def plot_ohlc(ohlc: pd.DataFrame, open_browser=True, show_legend=True):
    """
    Plot OHLC chart from dataframe
    Args:
        ohlc: dataframe
        open_browser: open html report in browser
        show_legend: show equity/pnl legend
    """
    backtest = Backtest(ohlc, strategy=Strategy, cash=10_000, commission=.002)
    backtest.run()
    backtest.plot(open_browser=open_browser, show_legend=show_legend)


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
