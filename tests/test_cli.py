import time
from unittest import TestCase

from click.testing import CliRunner

from jellyfish import cli


class TestCrawler(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCrawler, self).__init__(*args, **kwargs)
        self.runner = CliRunner()

    def test_call_with_no_args(self):
        self.runner.invoke(cli.crawler_cli, [])

    def test_wrong_argument(self):
        pair = 'bchbtc'

        result = self.runner.invoke(cli.crawler_cli, [
            '--start',
            pair,
            '--ttl', '1qq',
            '--block'])
        self.assertNotEqual(result.exit_code, 0)

        result = self.runner.invoke(cli.crawler_cli, [
            '--start',
            pair,
            '--period', '1q',
            '--block'])
        self.assertNotEqual(result.exit_code, 0)

    def test_start_stop(self):
        pair = 'bchbtc'
        pair1 = 'bchusdt'
        period = '1s'
        ttl = '10s'

        result = self.runner.invoke(cli.crawler_cli, ['--status'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), 'There is no active sessions.')

        result = self.runner.invoke(cli.crawler_cli, [
            '--start',
            pair, pair1,
            '--period', period,
            '--ttl', ttl,
            '--block'])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli.crawler_cli, [
            '--status',
            pair])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(pair.upper() in result.output)
        self.assertTrue(pair1.upper() in result.output)

        # TODO: CliRunner captures io streams which causes problems to service management
        time.sleep(3)
        result = self.runner.invoke(cli.crawler_cli, ['--stop', pair])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli.crawler_cli, ['--stop'])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli.crawler_cli, ['--status'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), 'There is no active sessions.')


class TestCandlesLoading(TestCase):
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
