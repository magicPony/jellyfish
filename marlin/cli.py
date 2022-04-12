"""
Command line interface communication
"""
import warnings
from datetime import datetime

import click
from dateutil import parser

from marlin import candles_loader, utils


def disable_warnings():
    """
    Disables all warnings
    """
    warnings.filterwarnings("ignore")


@click.command()
def clean_candles_cache():
    """
    Cleans candlestick cache directory
    """
    disable_warnings()
    candles_loader.clean_candles_cache()


@click.command()
@click.argument('pair')
@click.option('--from_date', '--from', required=True)
@click.option('--to_date', '--to', default=str(datetime.now().date()))
@click.option('--interval', '-i', required=True)
def download_candles(pair, from_date, to_date, interval):
    """
    Downloads candlestick history to cache
    Args:
        pair: trading pair
        from_date: start date
        to_date: end date
        interval: candle interval

    """
    disable_warnings()
    candles_loader.load_candles_history(
        client=utils.load_binance_client(),
        pair_sym=pair,
        start_dt=parser.parse(from_date),
        end_dt=parser.parse(to_date),
        interval=interval
    )
