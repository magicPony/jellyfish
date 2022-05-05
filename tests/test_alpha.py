from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Client

from jellyfish.alpha.indicators_stack_encoder import Indicator


class Test(TestCase):
    def test_fcn(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 3)
        df = load_candles_history(Client(), 'BTCUSDT', start_dt, end_dt, '1h')

        ind = Indicator()
        ind.fit(df)
        ind.transform(df)
