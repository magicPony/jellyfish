from datetime import datetime, timedelta
from unittest import TestCase

from backtesting import Backtest

from marlin.candles_loader import load_candles_history
from marlin.stretegy import DummyStrategy
from marlin.transform import to_heiken_ashi
from marlin.utils import load_binance_client, plot_ohlc


class Test(TestCase):
    def test_heiken_ashi(self):
        client = load_binance_client()
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(hours=400)
        pair = 'XRPUSDT'
        interval = '1h'
        frame = load_candles_history(client, pair, start_dt, end_dt, interval)

        to_heiken_ashi(frame)

        bt = Backtest(frame, DummyStrategy)
        bt.run()
        plot_ohlc(bt, open_browser=False)
