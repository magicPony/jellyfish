"""
Unicorn-Binance rest API manager wrapper
"""
from unicorn_binance_rest_api import BinanceRestApiManager

from jellyfish import utils


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
            creds = utils.load_binance_credentials()
            key = creds['key']
            secret = creds['secret']

        BinanceRestApiManager.__init__(self, api_key=key, api_secret=secret, exchange=exchange)
