import logging
from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish import transform
from jellyfish import utils
from jellyfish.candles_loader import load_candles_history


class TestTransform(TestCase):
    @staticmethod
    def load_sample_data():
        client = utils.load_binance_client()
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(hours=400)
        pair = 'XRPUSDT'
        interval = '1h'
        return load_candles_history(client, pair, start_dt, end_dt, interval)

    def test_heiken_ashi(self):
        frame = TestTransform.load_sample_data()
        transform.to_heiken_ashi(frame)
        utils.plot_ohlc(frame.reset_index())

    def test_log_prices(self):
        frame = TestTransform.load_sample_data()
        transform.to_log_prices(frame)
        utils.plot_ohlc(frame.reset_index())


class TestSampling(TestCase):
    @staticmethod
    def load_sample_data():
        client = utils.load_binance_client()
        pair = 'BTCUSDT'
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=365)
        interval = '15m'
        return load_candles_history(client, pair, start_dt, end_dt, interval)

    def test_tick_bars(self):
        frame = TestSampling.load_sample_data()
        frame = transform.sampling.tick_bars(frame.reset_index(), 2000000)
        utils.plot_ohlc(frame.reset_index())

    def test_line_break_bars(self):
        frame = TestSampling.load_sample_data().iloc[-10000:]
        frame = transform.sampling.line_break_bars(frame.reset_index(), 40)
        utils.plot_ohlc(frame.reset_index())

    def test_volume_bars(self):
        frame = TestSampling.load_sample_data()
        frame = transform.sampling.volume_bars(frame.reset_index(), 100000)
        utils.plot_ohlc(frame.reset_index())

    def test_renko(self):
        frame = TestSampling.load_sample_data()[-1000:]
        frame = transform.sampling.renko_bars(frame.reset_index())
        utils.plot_ohlc(frame)
