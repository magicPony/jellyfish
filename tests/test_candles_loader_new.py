from unittest import TestCase
from datetime import datetime, timedelta

from jellyfish.history_loader.candles_new import load_candles_history


class TestCandlesLoader(TestCase):
    def test_load(self):
        pair_sym = 'BTCUSDT'
        end_dt = datetime(year=2022, month=2, day=12)
        candles_num = 333
        interval = '1h'

        load_candles_history(pair_sym, end_dt=end_dt, interval=interval, candles_num=candles_num)

