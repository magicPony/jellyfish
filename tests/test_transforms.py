from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish.candles_loader import load_candles_history
from jellyfish.transform import to_heiken_ashi
from jellyfish.utils import load_binance_client, plot_ohlc


class Test(TestCase):
    def test_heiken_ashi(self):
        client = load_binance_client()
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(hours=400)
        pair = 'XRPUSDT'
        interval = '1h'
        frame = load_candles_history(client, pair, start_dt, end_dt, interval)

        to_heiken_ashi(frame)
        plot_ohlc(frame.reset_index())
