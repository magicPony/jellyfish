"""
Unicorn-Binance rest API manager wrapper
"""
import dotenv
import logging
from unicorn_binance_rest_api import BinanceRestApiManager

from jellyfish.constants import DOTENV_PATH


def _load_binance_credentials():  # pragma: no cover
    """
    Loads json with Binance API credentials
    :return: Binance (key, secret) pair
    """
    private_data = dotenv.dotenv_values(DOTENV_PATH)
    return private_data.get('BINANCE_KEY'), private_data.get('BINANCE_SECRET')


class Client(BinanceRestApiManager):
    """
    Binance rest manager client
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
            key, secret = _load_binance_credentials()
            logging.error('Unable to locate credentials! Fallback to demo user setup.')

        BinanceRestApiManager.__init__(self, api_key=key, api_secret=secret, exchange=exchange)
