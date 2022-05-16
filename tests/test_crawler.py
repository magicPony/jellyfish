import time
import pytest
from datetime import timedelta
from unittest import TestCase

from jellyfish.constants import ORDERBOOK_PATH
from jellyfish.crawler import Crawler
from jellyfish.crawler.daemon import Daemon


class TestCrawler(TestCase):
    def test_service(self):
        print('Creating service instance...')
        service = Daemon('debug_taras', pid_dir='/tmp')
        print('Pid', service.get_pid())
        assert not service.is_running()

        print('Service start...')
        service.start(True)
        assert service.is_running()

        print('Service teardown...')
        service.stop()
        assert not service.is_running()

    def test_crawler(self):
        sym = 'achbtc'

        out_path = ORDERBOOK_PATH / sym.upper()
        out_path.mkdir(exist_ok=True, parents=True)
        for p in out_path.iterdir():
            p.unlink()

        crawler = Crawler(sym)
        crawler.start(block=True)
        self.assertTrue(crawler.is_running())

        time.sleep(6)
        crawler.stop(block=True)
        self.assertFalse(crawler.is_running())

        self.assertGreater(len(list(out_path.iterdir())), 3)

    def test_run(self):
        sym = 'bchbtc'
        crawler = Crawler(sym, ttl=timedelta(seconds=5))
        crawler.run()

    def test_ttl(self):
        sym = 'bchbtc'
        ttl_secs = 3

        service = Crawler(sym, ttl=timedelta(seconds=ttl_secs))
        service.start(block=True)
        self.assertTrue(service.is_running())

        with pytest.raises(AttributeError):
            Crawler(sym, ttl=timedelta(days=1))

        time.sleep(ttl_secs + 1.5)
        self.assertFalse(service.is_running())
