import os
from unittest import TestCase
from click.testing import CliRunner

from jellyfish import cli

# TODO: fix syscall tests
# class TestSyscall(TestCase):
#     def test_clean_cache(self):
#         ret = os.system('rm-candles')
#         self.assertEqual(ret, 0)
#
#     def test_download_candles(self):
#         pair = 'BTCUSDT'
#         from_str = '2019-09-09'
#         interval = '4h'
#         cmd = f'load-candles {pair} --from {from_str} -i {interval}'
#
#         ret = os.system(cmd)
#         self.assertEqual(ret, 0)


class TestDirectCall(TestCase):
    def test_clean_cache(self):
        runner = CliRunner()
        result = runner.invoke(cli.clean_candles_cache)
        self.assertEqual(result.exit_code, 0)

    def test_download_candles(self):
        pair = 'BTCUSDT'
        from_str = '2019-09-09'
        interval = '1w'

        runner = CliRunner()
        result = runner.invoke(cli.download_candles, [
            pair,
            '--from_date', from_str,
            '--interval', interval
        ])

        self.assertEqual(result.exit_code, 0)



