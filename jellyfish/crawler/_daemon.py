"""
Basic daemon tool
"""
import os
import time
import logging

from service import Service


class Daemon(Service):
    """
    Daemon service
    """

    def stop(self, block=None):
        """
        Stop method that overrides base implementation and do a straightforward hard stop
        """
        # pylint: disable=protected-access
        if block is not None:
            # pragma: no cover
            logging.warning('Passing block argument is redundant')

        os.kill(self.get_pid(), 9)
        os.remove(self.pid_file._path)

    def run(self):
        """
        Dummy worker endless loop
        """
        # pylint: disable=no-self-use
        while True:
            time.sleep(1)
