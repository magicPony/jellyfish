from unittest import TestCase

from treasure_island.indicator import heiken_ashi
from treasure_island.candles_loader import get_sample_frame


class Test(TestCase):
    def test_heiken_ashi(self):
        df = get_sample_frame()
        ha = heiken_ashi(df)
