import logging
from dateutil import parser
from pandas.testing import assert_frame_equal

from unittest import TestCase

from treasure_island import CANDLES_HISTORY_PATH
from treasure_island.utils import load_binance_client
from treasure_island.candles_loader import load_candles_history, clean_candles_cache


class Test(TestCase):
    @staticmethod
    def load_for_interval(interval):
        client = load_binance_client()
        pair = 'XRPUSDT'
        start_dt = parser.parse('2021-01-09')
        end_dt = parser.parse('2021-09-09')
        interval = interval

        clean_candles_cache()
        assert len(list(CANDLES_HISTORY_PATH.iterdir())) == 0

        data = load_candles_history(client, pair, start_dt, end_dt, interval)
        assert len(data) > 0
        cached_data = load_candles_history(client, pair, start_dt, end_dt, interval)
        assert_frame_equal(data, cached_data)

    def test_load_btc_history_1d(self):
        Test.load_for_interval('1d')

    def test_load_btc_history_1h(self):
        Test.load_for_interval('1h')

    def test_load_binance_client(self):
        client = load_binance_client()
        logging.info(client.get_account())
