import time
from unittest import TestCase

from click.testing import CliRunner

from jellyfish import cli


class TestCrawler(TestCase):
    def test_wrong_argument(self):
        runner = CliRunner()

        pair = 'bchbtc'

        result = runner.invoke(cli.crawler_cli, [
            '--start',
            pair,
            '--ttl', '1qq',
            '--block'])
        self.assertNotEqual(result.exit_code, 0)

        result = runner.invoke(cli.crawler_cli, [
            '--start',
            pair,
            '--period', '1q',
            '--block'])
        self.assertNotEqual(result.exit_code, 0)

    def test_start_stop(self):
        runner = CliRunner()

        pair = 'bchbtc'
        period = '1s'
        ttl = '10s'

        result = runner.invoke(cli.crawler_cli, ['--status'])
        self.assertEqual(result.exit_code, 0)
        assert result.output.strip() == 'There is no active sessions.'

        result = runner.invoke(cli.crawler_cli, [
            '--start',
            pair,
            '--period', period,
            '--ttl', ttl,
            '--block'])
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(cli.crawler_cli, [
            '--status',
            pair])
        self.assertEqual(result.exit_code, 0)
        assert result.output.strip() == f'Active sessions list: {pair.upper()}'

        # TODO: CliRunner captures io streams which causes problems to service management
        time.sleep(4)
        result = runner.invoke(cli.crawler_cli, [pair])
        self.assertEqual(result.exit_code, 0)


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
