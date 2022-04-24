from unittest import TestCase

from dateutil import parser
from pandas.testing import assert_frame_equal

from jellyfish import CANDLES_HISTORY_PATH
from jellyfish.candles_loader import load_candles_history, clean_candles_cache
from jellyfish.core import Client


class Test(TestCase):
    def load_for_interval(self, interval):
        client = Client()
        pair = 'XRPUSDT'
        start_dt = parser.parse('2021-01-09 12:22')
        end_dt = parser.parse('2021-09-09 10:00')
        interval = interval

        clean_candles_cache()
        self.assertEqual(len(list(CANDLES_HISTORY_PATH.iterdir())), 0)

        data = load_candles_history(client, pair, start_dt, end_dt, interval)
        self.assertGreater(len(data), 0)

        cached_data = load_candles_history(None, pair, start_dt, end_dt, interval)
        assert_frame_equal(data, cached_data)

    def test_load_btc_history_1d(self):
        self.load_for_interval('1d')

    def test_load_btc_history_1h(self):
        self.load_for_interval('1h')

    def test_load_binance_client(self):
        client = Client()
        client.ping()
