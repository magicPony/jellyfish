from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish import transform, utils
from jellyfish.transform import sampling
from jellyfish.history_loader import load_candles_history
from jellyfish.core import Client


class TestTransform(TestCase):
    @staticmethod
    def load_sample_data():
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(hours=400)
        return load_candles_history('XRPUSDT', start_dt, end_dt, '1h')

    def test_heiken_ashi(self):
        frame = TestTransform.load_sample_data()
        transform.to_heiken_ashi(frame)
        utils.plot_ohlc(frame)

    def test_log_prices(self):
        frame = TestTransform.load_sample_data()
        transform.to_log_prices(frame)
        utils.plot_ohlc(frame)


class TestSampling(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=30)
        self.frame = load_candles_history('BTCUSDT', start_dt, end_dt, '15m')

    def test_tick_bars(self):
        frame = self.frame
        frame = sampling.tick_bars(frame, 3e5)
        utils.plot_ohlc(frame)

    def test_line_break_bars(self):
        frame = self.frame
        frame = sampling.line_break_bars(frame, 10)
        utils.plot_ohlc(frame)

    def test_volume_bars(self):
        frame = self.frame
        frame = sampling.volume_bars(frame, 2e3)
        utils.plot_ohlc(frame)

    def test_renko(self):
        frame = self.frame
        frame = sampling.renko_bars(frame, 100)
        utils.plot_ohlc(frame)

    def test_dollars(self):
        frame = self.frame
        frame = sampling.dollar_bars(frame, 1e8)
        utils.plot_ohlc(frame)

    def test_tick_imbalance(self):
        frame = self.frame
        frame = sampling.tick_imbalance(frame, 7)
        utils.plot_ohlc(frame)

    def test_compose(self):
        t = transform.compose([
            (sampling.line_break_bars, 4),
            (sampling.volume_bars, 1.5e3),
            (sampling.tick_imbalance, 2),
            transform.to_heiken_ashi,
            transform.to_log_prices,
            (sampling.tick_imbalance, 2),
            (sampling.volume_bars, 2e4),
            (sampling.line_break_bars, 2),
            (sampling.renko_bars, 1e-2)
        ])

        frame = self.frame
        frame = t(frame)

        utils.plot_ohlc(frame)
