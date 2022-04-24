from unittest import TestCase

import numpy as np
import pandas as pd

from jellyfish import utils


class Test(TestCase):
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

