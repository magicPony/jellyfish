"""
Utility functions
"""
import json
import logging
from tempfile import TemporaryDirectory

from backtesting import Backtest
from unicorn_binance_rest_api import BinanceRestApiManager as RestManager

from treasure_island import PRIVATE_DATA_PATH


def load_binance_credentials():
    """
    Loads json with Binance API credentials
    :return: json with creds
    """
    try:
        with (PRIVATE_DATA_PATH / 'binance_creds.json').open() as creds_file:
            return json.load(creds_file)

    except FileNotFoundError as exc:
        logging.warning(exc)
        return None


def plot_ohlc(backtest: Backtest, filepath=None, open_browser=True):
    """
    Plots candlestick chart from dataframe
    @param backtest:
    @param filepath:
    @param open_browser:
    @return:
    """
    with TemporaryDirectory() as temp_dir:
        if filepath is None:
            filepath = f'{temp_dir.name}/test.html'

        backtest.plot(filename=filepath, show_legend=False, open_browser=open_browser)
        temp_dir.cleanup()


def load_binance_client():
    """
    Loads Binace reset manager client
    :return: RestManager client
    """
    creds = load_binance_credentials()
    return RestManager(creds['key'], creds['secret'])
