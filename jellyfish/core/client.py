"""
Unicorn-Binance rest API manager wrapper
"""
import logging
import json

from unicorn_binance_rest_api import BinanceRestApiManager

from jellyfish.constants import PRIVATE_DATA_PATH


def _load_binance_credentials():  # pragma: no cover
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


class Client(BinanceRestApiManager):
    """
    Binance reset manager client
    """
    SPOT_EXCHANGE = 'binance.com'
    FUTURES_EXCHANGE = 'binance.com-futures'

    def __init__(self, demo_user=False, exchange=SPOT_EXCHANGE):
        """
        Rest manager initialization
        Args:
            demo_user: restrict user to demo account
            exchange: exchange environment e.g. spot/futures
        """
        key = None
        secret = None
        if not demo_user:
            creds = _load_binance_credentials()
            key = creds['key']
            secret = creds['secret']

        try:
            BinanceRestApiManager.__init__(self, api_key=key, api_secret=secret, exchange=exchange)
        except ConnectionError:
            BinanceRestApiManager.__init__(self, api_key=None, api_secret=None, exchange=exchange)
            logging.warning('Set demo user as fallback setup due to problems with internet')
