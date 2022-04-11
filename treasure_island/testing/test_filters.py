from datetime import datetime, timedelta
from tempfile import TemporaryDirectory
from unittest import TestCase

from backtesting import Backtest

from treasure_island.candles_loader import load_candles_history
from treasure_island.filters import to_heiken_ashi
from treasure_island.testing import DummyStrategy
from treasure_island.utils import load_binance_client


class Test(TestCase):
    def test_heiken_ashi(self):
        client = load_binance_client()
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(hours=400)
        pair = 'XRPUSDT'
        interval = '1h'
        frame = load_candles_history(client, pair, start_dt, end_dt, interval)
        frame1 = load_candles_history(client, pair, start_dt, end_dt, interval)

        to_heiken_ashi(frame)

        bt = Backtest(frame, DummyStrategy)
        bt.run()
        with TemporaryDirectory() as temp_dir:
            bt.plot(filename=f'{temp_dir}/test.html', show_legend=False)
