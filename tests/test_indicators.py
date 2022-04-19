from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish import utils, indicator
from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Backtest, Strategy


class DummyStrategyWithIndicators(Strategy):
    def init(self):
        self.mark_as_indicator('zigzag')
        self.mark_as_indicator('hurst_random_walk')
        self.mark_as_indicator('hurst_change')
        self.mark_as_indicator('hurst_price')


class Test(TestCase):
    def test_indicators(self):
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(days=30)
        frame = load_candles_history(utils.load_binance_client(), 'BTCUSDT', start_dt, end_dt, '1h')

        frame['zigzag'] = indicator.zigzag(frame.Close.to_numpy(), 2e-2)
        frame['hurst_random_walk'] = indicator.hurst(frame.Close.to_numpy(), 200, 'random_walk')
        frame['hurst_change'] = indicator.hurst(frame.Close.to_numpy(), 100, 'change')
        frame['hurst_price'] = indicator.hurst(frame.Close.to_numpy(), 200, 'price')

        backtest = Backtest(frame.reset_index(), DummyStrategyWithIndicators)
        backtest.run()
        backtest.plot()

