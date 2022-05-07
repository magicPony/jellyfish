from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish.alpha.indicators_stack_encoder import Indicator
from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Client, Strategy, Backtest


class MlStrategy(Strategy):
    def init(self):
        self.change_thr = 0.015
        self.signal = self.I(lambda x: x, self.data.df.signal)

    def next(self):
        high_exit = self.data.Close * (1 + self.change_thr)
        low_exit = self.data.Close * (1 - self.change_thr)

        if self.signal > 0:
            self.position.close()
            # self.buy(sl=low_exit, tp=high_exit)
        elif self.signal < 0:
            self.position.close()
            self.sell(tp=low_exit, sl=high_exit)


class Test(TestCase):
    def test_fcn(self):
        end_dt = datetime(year=2022, month=4, day=3)
        start_dt = end_dt - timedelta(days=30 * 3)
        df = load_candles_history(Client(), 'BTCUSDT', start_dt, end_dt, '1h').reset_index()

        change_thr = 0.015
        indicator = Indicator(change_thr=change_thr, depth=5)
        indicator.fit(df.reset_index())
        # df['signal'] = indicator.transform(df.reset_index())
        #
        # bt = Backtest(df, MlStrategy, cash=1e6)
        # stats = bt.run()
        # bt.plot(open_browser=True)
        # print(stats)
