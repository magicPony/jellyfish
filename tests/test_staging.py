from datetime import datetime, timedelta
from unittest import TestCase

from backtesting import Backtest

from jellyfish.candles_loader import load_candles_history
from jellyfish.stretegy import SmaCross
from jellyfish import utils, transform, indicator


class SmaCrossWithIndicators(SmaCross):
    def init(self):
        self.hurst = self.I(indicator.hurst, self.data.Close, kind='price', name='Hurst (price)', overlay=False)
        self.I(indicator.hurst, self.data.Close, kind='random_walk', name='Hurst (random walk)', overlay=False)
        self.I(indicator.hurst, self.data.Close, kind='change', name='Hurst (change)', overlay=False)

        super(SmaCrossWithIndicators, self).init()

    def next(self):
        if self.hurst > 0.525:
            super(SmaCrossWithIndicators, self).next()


class Test(TestCase):
    def test_heiken_ashi_strategy(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 16)
        frame = load_candles_history(utils.load_binance_client(), 'XRPUSDT', start_dt, end_dt, '1h')

        # fucking "summer time" +-one hour causing problems with timestamps
        frame = frame.reset_index()
        frame.Date = frame.Date.dt.date
        frame.set_index('Date', inplace=True)

        t = transform.compose([
            (transform.sampling.tick_imbalance, 10),
        ])
        frame = t(frame.reset_index())

        SmaCrossWithIndicators.n1 = 10
        SmaCrossWithIndicators.n2 = 30
        bt = Backtest(frame, SmaCrossWithIndicators, cash=10_000, commission=.002)
        stats = bt.run()
        utils.plot_ohlc_from_backtest(bt)

        self.assertGreater(stats['# Trades'], 0)
