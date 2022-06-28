from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish.history_loader import load_candles_history
from jellyfish.core import Client
from jellyfish.core.backtest import _get_ticks_per_year


class TestClient(TestCase):
    def test_client_creation(self):
        Client()
        Client(demo_user=True)

    def test_ticks_per_year(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 16 * 2)
        frame = load_candles_history('XRPUSDT', start_dt, end_dt, '1d')

        self.assertIsNotNone(_get_ticks_per_year(frame))
        self.assertIsNotNone(_get_ticks_per_year(frame.reset_index()))
        self.assertIsNone(_get_ticks_per_year(frame.reset_index(drop=True)))
