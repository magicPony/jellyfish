from unittest import TestCase
from datetime import datetime, timedelta

from jellyfish.history_loader import load_orderbook_history, load_candles_history
from jellyfish.core import Client
from jellyfish.constants import ORDERBOOK


class Test(TestCase):
    def test_load(self):
        pair = 'btcusdt'
        start_dt = datetime(year=2021, month=6, day=16)
        end_dt = start_dt + timedelta(days=1)

        orderbook = load_orderbook_history(pair, start_dt=start_dt, end_dt=end_dt)[ORDERBOOK]
        candles = load_candles_history(Client(), pair, start_dt, end_dt, interval='1m')

        df = candles.join(orderbook)
        print(df.head())
