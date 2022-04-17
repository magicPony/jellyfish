from datetime import datetime, timedelta
from unittest import TestCase

from backtesting import Backtest

from jellyfish import utils, indicator
from jellyfish.candles_loader import load_candles_history
from jellyfish.stretegy import DummyStrategy


class DummyStrategyWithZigzag(DummyStrategy):
    def init(self):
        self.I(indicator.zigzag, self.data.Close.data, 2e-2)


class Test(TestCase):
    def test_zigzag(self):
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(days=30)
        frame = load_candles_history(utils.load_binance_client(), 'XRPUSDT', start_dt, end_dt, '1h')

        backtest = Backtest(frame.reset_index(), DummyStrategyWithZigzag)
        backtest.run()
        utils.plot_ohlc_from_backtest(backtest)
