from datetime import datetime, timedelta
from unittest import TestCase

import numpy as np
import pandas as pd

from jellyfish import utils
from jellyfish.candles_loader import load_candles_history


class Test(TestCase):
    def test_client(self):
        utils.load_binance_client()

    def test_ticks_per_year(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 16 * 2)
        frame = load_candles_history(utils.load_binance_client(), 'XRPUSDT', start_dt, end_dt, '1d')

        self.assertIsNotNone(utils.get_ticks_per_year(frame))
        self.assertIsNotNone(utils.get_ticks_per_year(frame.reset_index()))
        self.assertIsNone(utils.get_ticks_per_year(frame.reset_index(drop=True)))

    def test_downsample_candle(self):
        numbers = [1, 2, 3, 4, 5, 6]
        data = pd.DataFrame({
            'a': numbers,
            'b': numbers,
            'c': numbers,
            'd': numbers
        })
        downsampled_data = utils.collapse_candle(data, {
            'a': np.max,
            'b': np.mean,
            'c': utils.first,
            'd': 'sum'
        })

        self.assertEqual(downsampled_data, [6, 3.5, 1, 21])

