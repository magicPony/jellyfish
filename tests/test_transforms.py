from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish import transform, utils
from jellyfish.candles_loader import load_candles_history


class TestTransform(TestCase):
    @staticmethod
    def load_sample_data():
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(hours=400)
        return load_candles_history(utils.load_binance_client(), 'XRPUSDT', start_dt, end_dt, '1h')

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
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=365)
        return load_candles_history(utils.load_binance_client(), 'XRPUSDT', start_dt, end_dt, '15m')

    def test_tick_bars(self):
        frame = TestSampling.load_sample_data()
        frame = transform.sampling.tick_bars(frame.reset_index(), 2e6)
        utils.plot_ohlc(frame.reset_index())

    def test_line_break_bars(self):
        frame = TestSampling.load_sample_data().iloc[-10000:]
        frame = transform.sampling.line_break_bars(frame.reset_index(), 40)
        utils.plot_ohlc(frame.reset_index())

    def test_volume_bars(self):
        frame = TestSampling.load_sample_data()[-1000:]
        frame = transform.sampling.volume_bars(frame.reset_index(), 2e3)
        utils.plot_ohlc(frame.reset_index())

    def test_renko(self):
        frame = TestSampling.load_sample_data()[-1000:]
        frame = transform.sampling.renko_bars(frame.reset_index())
        utils.plot_ohlc(frame)

    def test_dollars(self):
        frame = TestSampling.load_sample_data()[-1000:]
        frame = transform.sampling.dollar_bars(frame.reset_index(), 1e8)
        utils.plot_ohlc(frame)

    def test_tick_imbalance(self):
        frame = TestSampling.load_sample_data()[-1000:]
        frame = transform.sampling.tick_imbalance(frame.reset_index(), 7)
        utils.plot_ohlc(frame)

    def test_zigzag(self):
        frame = TestSampling.load_sample_data()
        frame = transform.sampling.zigzag(frame.reset_index(), 3e-1)
        utils.plot_ohlc(frame)
