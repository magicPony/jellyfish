import os
from unittest import TestCase
from click.testing import CliRunner

from treasure_island import cli


class TestSyscall(TestCase):
    def test_clean_cache(self):
        assert os.system('rm-candles') == 0

    def test_download_candles(self):
        pair = 'BTCUSDT'
        from_str = '2019-09-09'
        interval = '4h'
        cmd = f'load-candles {pair} --from {from_str} -i {interval}'

        assert os.system(cmd) == 0


class TestDirectCall(TestCase):
    def test_clean_cache(self):
        runner = CliRunner()
        result = runner.invoke(cli.clean_candles_cache)
        assert result.exit_code == 0

    def test_download_candles(self):
        pair = 'BTCUSDT'
        from_str = '2019-09-09'
        interval = '4h'

        runner = CliRunner()
        result = runner.invoke(cli.download_candles, [
            pair,
            '--from_date', from_str,
            '--interval', interval
        ])

        assert result.exit_code == 0



