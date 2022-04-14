from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish.candles_loader import load_candles_history
from jellyfish.transform import feature, sampling
from jellyfish.utils import load_binance_client, plot_ohlc


def load_sample_data():
    client = load_binance_client()
    end_dt = datetime(year=2022, month=2, day=3)
    start_dt = end_dt - timedelta(hours=400)
    pair = 'XRPUSDT'
    interval = '1h'
    return load_candles_history(client, pair, start_dt, end_dt, interval)


class TestFeatures(TestCase):
    def test_heiken_ashi(self):
        frame = load_sample_data()
        feature.to_heiken_ashi(frame)
        plot_ohlc(frame.reset_index())

    def test_log_prices(self):
        frame = load_sample_data()
        feature.to_log_prices(frame)
        plot_ohlc(frame.reset_index())


class TestSampling(TestCase):
    def test_tick_bars(self):
        client = load_binance_client()
        pair = 'BTCUSDT'
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=365)
        interval = '15m'

        frame = load_candles_history(client, pair, start_dt, end_dt, interval)
        frame = sampling.to_tick_bars(frame, 2000000)
        plot_ohlc(frame.reset_index())
