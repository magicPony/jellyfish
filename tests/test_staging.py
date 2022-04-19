from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish import utils, transform, indicator
from jellyfish.alpha import SmaCross
from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Backtest


class SmaCrossWithIndicators(SmaCross):
    def init(self):
        self.hurst = self.I(indicator.hurst, self.data.Close, kind='price',
                            name='Hurst (price)', overlay=False)
        self.I(indicator.hurst, self.data.Close, kind='random_walk',
               name='Hurst (random walk)', overlay=False)
        self.I(indicator.hurst, self.data.Close, kind='change',
               name='Hurst (change)', overlay=False)
        self.I(indicator.rsi, self.data.Close, 20, overlay=False)

        super(SmaCrossWithIndicators, self).init()

    def next(self):
        if self.hurst > 0.6:
            super(SmaCrossWithIndicators, self).next()


class Test(TestCase):
    def test_heiken_ashi_strategy(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 16 * 2)
        frame = load_candles_history(utils.load_binance_client(), 'XRPUSDT', start_dt, end_dt, '1h')

        t = transform.compose([
            (transform.sampling.tick_imbalance, 10),
        ])
        frame = t(frame.reset_index())

        SmaCrossWithIndicators.n1 = 10
        SmaCrossWithIndicators.n2 = 30
        bt = Backtest(frame, SmaCrossWithIndicators)
        stats = bt.run()
        bt.plot()

        self.assertGreater(stats['# Trades'], 0)
        print(stats)
