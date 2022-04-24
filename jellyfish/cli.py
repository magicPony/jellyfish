"""
Command line interface communication
"""
from datetime import datetime

import click
from dateutil import parser

from jellyfish import candles_loader, utils
from jellyfish.core import Client


@click.command()
def clean_candles_cache():
    """
    Cleans candlestick cache directory
    """
    utils.disable_warnings()
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
    utils.disable_warnings()
    candles_loader.load_candles_history(
        client=Client(),
        pair_sym=pair,
        start_dt=parser.parse(from_date),
        end_dt=parser.parse(to_date),
        interval=interval
    )
