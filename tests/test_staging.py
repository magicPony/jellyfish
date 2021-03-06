from datetime import datetime, timedelta
from unittest import TestCase

import pandas as pd

from jellyfish import transform, indicator
from jellyfish.core import Backtest
from jellyfish.core.strategy import SmaCross, BuyAndHold
from jellyfish.history_loader import load_candles_history
from jellyfish.transform import sampling


# noinspection PyAttributeOutsideInit
class SmaCrossWithIndicators(SmaCross):
    def init(self):
        self.hurst = self.I(indicator.hurst, self.data.Close, kind='price',
                            name='Hurst (price)', overlay=False)
        self.I(indicator.hurst, self.data.Close, kind='random_walk',
               name='Hurst (random walk)', overlay=False)
        self.I(indicator.hurst, self.data.Close, kind='change',
               name='Hurst (change)', overlay=False)
        self.I(indicator.rsi, self.data.Close, 20, overlay=False)

        SmaCross.init(self)

    def next(self):
        if self.hurst > 0.6:
            super(SmaCrossWithIndicators, self).next()


class Test(TestCase):
    def test_heiken_ashi_strategy(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 3)
        frame = load_candles_history('XRPUSDT', start_dt, end_dt, '1h')

        bt = Backtest(frame, BuyAndHold)
        columns = ['Sharpe Ratio', 'Calmar Ratio', 'Sortino Ratio']
        buy_n_hold_stats = bt.run()
        stats = [buy_n_hold_stats[columns].tolist()]

        self.assertGreater(buy_n_hold_stats['# Trades'], 0)

        t = transform.compose([
            (sampling.tick_imbalance, 10),
        ])
        frame = t(frame)

        SmaCrossWithIndicators.n1 = 10
        SmaCrossWithIndicators.n2 = 30
        bt = Backtest(frame, SmaCrossWithIndicators)
        sma_cross_stats = bt.run()
        stats.append(sma_cross_stats[columns].tolist())
        bt.plot()

        self.assertGreater(sma_cross_stats['# Trades'], 0)

        stats = pd.DataFrame(stats, columns=columns, index=['BuyAndHold', 'SmcCrossover'])
        print(stats)
