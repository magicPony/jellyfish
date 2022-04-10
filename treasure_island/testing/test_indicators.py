from unittest import TestCase

from backtesting import Strategy, Backtest
from backtesting.test import SMA
from backtesting.lib import crossover

from treasure_island.indicators import heiken_ashi
from treasure_island.candles_loader import get_sample_frame

from tempfile import TemporaryDirectory


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 50
    n2 = 200

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

        self.I(heiken_ashi, self.data.df, name='Heiken Ashi')

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

        else:
            pass


class Test(TestCase):
    def test_heiken_ashi(self):
        frame = get_sample_frame()
        bt = Backtest(frame, SmaCross, cash=10_000, commission=.002)
        stats = bt.run()
        print(stats)

        with TemporaryDirectory() as temp_dir:
            bt.plot(filename=f'{temp_dir}/test.html', plot_pl=True, plot_return=True, plot_equity=True)

