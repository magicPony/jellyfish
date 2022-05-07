from datetime import datetime, timedelta
from unittest import TestCase

import numpy as np

from jellyfish.alpha.indicators_stack_encoder import Indicator
from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Client, Strategy, Backtest

POSITION_CHANGE_FACTOR = 0.01
TRAIN_CHANGE_FACTOR = 0.015
CANDLES_DEPTH = 3


class MlStrategy(Strategy):
    def init(self):
        indicator = Indicator(change_thr=TRAIN_CHANGE_FACTOR, depth=CANDLES_DEPTH)
        self.signal = self.I(indicator.fit_transform, self.data.df.reset_index(), name='Algo signal')

    def next(self):
        high_exit = self.data.Close * (1 + POSITION_CHANGE_FACTOR)
        low_exit = self.data.Close * (1 - POSITION_CHANGE_FACTOR)

        if self.signal[-1] is np.NAN:
            return
        if self.signal > 0:
            self.position.close()
            self.buy(sl=low_exit, tp=high_exit)
        elif self.signal < 0:
            self.position.close()
            self.sell(tp=low_exit, sl=high_exit)


class Test(TestCase):
    def test_fcn(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 3)
        df = load_candles_history(Client(), 'BTCUSDT', start_dt, end_dt, '1h').reset_index()

        bt = Backtest(df.set_index('Date'), MlStrategy, cash=1e6)
        stats = bt.run()
        bt.plot(open_browser=True)
        print(stats)
