from datetime import datetime, timedelta
from unittest import TestCase

from dateutil import parser
from pandas.testing import assert_frame_equal

from jellyfish.core import Client
from jellyfish.history_loader import (load_candles_history, clean_candles_cache,
                                      get_sample_frame)


class TestOrderbookLoader(TestCase):
    def test_load(self):
        pair = 'BTCUSDT'
        start_dt = datetime(year=2021, month=6, day=16)
        end_dt = start_dt + timedelta(days=1)

        load_candles_history(pair, start_dt, end_dt, interval='1m', read_orderbook=True)


class TestCandlesLoader(TestCase):
    def load_for_interval(self, interval, window_size: timedelta):
        pair = 'XRPUSDT'
        start_dt = parser.parse('2021-01-09 12:22')
        end_dt = start_dt + window_size
        interval = interval

        clean_candles_cache()
        self.assertIsNone(get_sample_frame())

        data = load_candles_history(pair, start_dt, end_dt, interval, client=Client())
        self.assertGreater(len(data), 0)

        cached_data = load_candles_history(pair, start_dt, end_dt, interval, client=None)  # offline mode simulation
        assert_frame_equal(data, cached_data)

    def test_load_btc_history_1d(self):
        self.load_for_interval('1d', timedelta(days=240))

    def test_load_btc_history_1h(self):
        self.load_for_interval('1h', timedelta(hours=240))

    def test_get_sample_frame(self):
        clean_candles_cache()
        self.assertIsNone(get_sample_frame())

        load_candles_history('XRPUSDT', parser.parse('2021-01-08 12:22'), parser.parse('2021-01-09 12:22'), '1h')
        self.assertIsNotNone(get_sample_frame())

        max_records = 3
        data = get_sample_frame(max_records=max_records)
        self.assertEqual(len(data), max_records)


    def test_define_candles_num(self):
        candles_num = 123
        pair_sym = 'XRPUSDT'
        df = load_candles_history(pair_sym, start_dt=parser.parse('2021-01-08 12:22'),
                                  candles_num=candles_num, interval='1h')
        self.assertEqual(len(df), candles_num)

        df = load_candles_history(pair_sym, end_dt=parser.parse('2021-01-08 12:22'),
                                  candles_num=candles_num, interval='1h')
        self.assertEqual(len(df), candles_num)

    def test_load_binance_client(self):
        client = Client()
        client.ping()
