"""
Command line interface communication
"""
import logging
from datetime import datetime, timedelta

import click
from dateutil import parser
from pytimeparse.timeparse import timeparse

from jellyfish import utils
from jellyfish.core import Client
from jellyfish.crawler import Crawler
from jellyfish.history_loader import load_candles_history, clean_candles_cache


@click.command(context_settings={
    'ignore_unknown_options': True
})
@click.argument('pairs_list', nargs=-1, type=click.UNPROCESSED)
@click.option('--start', is_flag=True)
@click.option('--status', is_flag=True)
@click.option('--stop', is_flag=True)
@click.option('--period', '-p', default='1m')
@click.option('--ttl', default='720h')  # e.g. 720 hours(roughly one month)
@click.option('--block', is_flag=True)
def crawler_cli(pairs_list, start, status, stop, period, ttl, block):
    if start:
        try:
            ttl = timedelta(seconds=timeparse(ttl))
        except TypeError:
            logging.fatal('Unable to parse ttl with value=`%s`', ttl)
            return

        try:
            period = timedelta(seconds=timeparse(period))
        except TypeError:
            logging.fatal('Unable to parse period with value=`%s`', period)
            return

        for pair in pairs_list:
            Crawler(pair, period, ttl).start(block=block)

    elif status:
        active_sessions = Crawler.active_sessions()
        if len(active_sessions) > 0:
            print('Active sessions list:', ' '.join(active_sessions))
        else:
            print('There is no active sessions.')

    elif stop:
        for pair in pairs_list:
            crawler = Crawler(pair)
            if crawler.is_running():
                crawler.stop()
            else:
                print('No active sessions associated with token were found.')

        if len(pairs_list) == 0:
            Crawler.stop_all()

    else:
        logging.error('No action argument provided. '
                      'Possible actions: start|status|stop')


@click.command()
def clean_candles_cache():
    """
    Cleans candlestick cache directory
    """
    utils.disable_warnings()
    clean_candles_cache()


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
    load_candles_history(
        client=Client(),
        pair_sym=pair,
        start_dt=parser.parse(from_date),
        end_dt=parser.parse(to_date),
        interval=interval
    )
