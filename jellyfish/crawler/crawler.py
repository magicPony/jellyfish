"""
Crawler daemon
"""
import json
import time
from datetime import timedelta, datetime
from pathlib import Path

import psutil
import requests

from jellyfish.constants import ORDERBOOK_PATH
from jellyfish.crawler.daemon import Daemon

EXIT_CODE_OK = 200
JELLY_CRAWLER = 'jelly_crawler'
REQUEST_URI_PATTERN = 'https://www.binance.com/api/v3/depth?symbol=%s&limit=5000'
PID_DIR = Path('/tmp')


class Crawler(Daemon):
    """
    Crawler daemon
    """
    RETRY_TIMEOUT = timedelta(seconds=1)

    def __init__(self, pair: str, poll_period: timedelta = None, ttl: timedelta = None):
        """
        Initialize daemon
        Args:
            pair: trading pair
            poll_period: update period
        """
        pair = pair.upper()
        filename = f'{JELLY_CRAWLER}_{pair}'
        super().__init__(filename, pid_dir=PID_DIR.absolute())

        if self.is_running() and ttl is not None:
            raise AttributeError('Passing `ttl` argument to crawler service that associated '
                                 'with a running process is ambiguous')

        self.start_time = datetime.now()
        self.ttl = ttl
        self.out_dir_path = ORDERBOOK_PATH / pair
        self.request_uri = REQUEST_URI_PATTERN % pair
        self.poll_period = poll_period or timedelta(seconds=1)

        self.out_dir_path.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def stop_all():
        """
        Stop all crawler sessions
        """
        for pidfile in PID_DIR.glob(f'*{JELLY_CRAWLER}*'):
            pair = pidfile.name.replace(f'{JELLY_CRAWLER}_', '').split('.')[0]
            Crawler(pair).stop()

    @staticmethod
    def active_sessions():
        """
        Get list of all active sessions
        Returns: active sessions list
        """
        active_sessions = []
        for pidfile_path in PID_DIR.glob(f'*{JELLY_CRAWLER}*'):
            proc_name = pidfile_path.name.split('.', maxsplit=1)[0]
            with pidfile_path.open() as pidfile:
                pid = int(pidfile.read())

            if psutil.Process(pid).name() == proc_name:
                pair = proc_name.replace(f'{JELLY_CRAWLER}_', '')
                active_sessions.append(pair)

        return active_sessions

    def run(self):
        """
        Poll stream data and create a dump
        Returns: exit code
        """
        now = datetime.now()
        if self.ttl is not None and self.start_time + self.ttl < now:
            return self.stop(block=True)

        response = requests.get(self.request_uri)
        if response.status_code != EXIT_CODE_OK:
            time.sleep(self.RETRY_TIMEOUT.seconds)
            return self.run()

        content: json = response.content.decode()
        timestamp = int(datetime.now().timestamp())
        with (self.out_dir_path / f'{timestamp}.json').open('w') as dump_file:
            json.dump(content, dump_file)

        time.sleep(self.poll_period.seconds)
        self.run()
        return EXIT_CODE_OK
