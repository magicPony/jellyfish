import os
from unittest import TestCase


class Test(TestCase):
    def test_clean_cache(self):
        assert os.system('rm-candles') == 0

    def test_download_candles(self):
        pair = 'BTCUSDT'
        from_str = '2019-09-09'
        interval = '4h'
        cmd = f'load-candles {pair} --from {from_str} -i {interval}'

        assert os.system(cmd) == 0

