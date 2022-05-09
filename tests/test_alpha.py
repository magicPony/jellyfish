from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish.alpha.indicators_stack_encoder import Indicator
from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Client, Strategy, Backtest

POSITION_CHANGE_FACTOR = 0.01
TRAIN_CHANGE_FACTOR = 0.015
CANDLES_DEPTH = 3


class MlStrategy(Strategy):
    algo = None

    def init(self):
        self.signal = self.I(self.algo.transform, self.data.df.reset_index(),
                             name='Algo signal', overlay=False)

    def next(self):
        if len(self.signal) < 2:
            return

        if self.signal > 0 > self.signal[-2]:
            self.position.close()
            self.buy()
        elif self.signal < 0 < self.signal[-2]:
            self.position.close()
            self.sell()


class Test(TestCase):
    def test_fcn(self):
        train_size = 2000
        val_size = 800

        client = Client()
        interval = '1h'
        pair = 'XRPUSDT'

        mid_dt = datetime(year=2022, month=1, day=3)
        train_df = load_candles_history(client=client, pair_sym=pair, start_dt=mid_dt,
                                        interval=interval, candles_num=train_size)

        val_df = load_candles_history(client=client, pair_sym=pair, end_dt=mid_dt,
                                      interval=interval, candles_num=val_size)

        indicator = Indicator(change_thr=TRAIN_CHANGE_FACTOR, depth=CANDLES_DEPTH)
        indicator.fit(train_df)
        MlStrategy.algo = indicator

        bt = Backtest(val_df, MlStrategy, trade_on_close=True)
        stats = bt.run()
        bt.plot(open_browser=True)
        print(stats)
