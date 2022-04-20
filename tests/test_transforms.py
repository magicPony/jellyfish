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
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=30 * 6)
        self.frame = load_candles_history(utils.load_binance_client(), 'BTCUSDT', start_dt, end_dt, '15m')

    def test_tick_bars(self):
        frame = self.frame
        frame = transform.sampling.tick_bars(frame.reset_index(), 2e6)
        utils.plot_ohlc(frame.reset_index())

    def test_line_break_bars(self):
        frame = self.frame.iloc[-10000:]
        frame = transform.sampling.line_break_bars(frame.reset_index(), 40)
        utils.plot_ohlc(frame.reset_index())

    def test_volume_bars(self):
        frame = self.frame[-1000:]
        frame = transform.sampling.volume_bars(frame.reset_index(), 2e3)
        utils.plot_ohlc(frame.reset_index())

    def test_renko(self):
        frame = self.frame[-1000:]
        frame = transform.sampling.renko_bars(frame.reset_index(), 100)
        utils.plot_ohlc(frame)

    def test_dollars(self):
        frame = self.frame[-1000:]
        frame = transform.sampling.dollar_bars(frame.reset_index(), 1e8)
        utils.plot_ohlc(frame)

    def test_tick_imbalance(self):
        frame = self.frame[-1000:]
        frame = transform.sampling.tick_imbalance(frame.reset_index(), 7)
        utils.plot_ohlc(frame)

    def test_zigzag(self):
        frame = self.frame
        frame = transform.sampling.zigzag(frame.reset_index(), 3e-1)
        utils.plot_ohlc(frame)

    def test_compose(self):
        t = transform.compose([
            (transform.sampling.line_break_bars, 40),
            (transform.sampling.volume_bars, 2e3),
            (transform.sampling.tick_imbalance, 7),
            transform.to_heiken_ashi,
            transform.to_log_prices,
            transform.to_heiken_ashi,
            (transform.sampling.tick_imbalance, 2),
            (transform.sampling.volume_bars, 5e5),
            (transform.sampling.line_break_bars, 2),
            (transform.sampling.renko_bars, 5e-2)
        ])

        frame = self.frame
        frame = t(frame.reset_index())

        utils.plot_ohlc(frame)
