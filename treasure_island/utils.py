"""
Utility functions
"""
import json
import logging

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


def load_binance_client():
    """
    Loads Binace reset manager client
    :return: RestManager client
    """
    creds = load_binance_credentials()
    return RestManager(creds['key'], creds['secret'])
