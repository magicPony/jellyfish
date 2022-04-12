# pylint: disable=W0201

"""
Strategies list
"""

from backtesting import Strategy
from backtesting.test import SMA
from backtesting.lib import crossover


class DummyStrategy(Strategy):
    """
    Dummy empty strategy
    """
    def init(self):
        pass

    def next(self):
        pass


class SmaCross(Strategy):
    """
    Simple moving average crossover strategy
    """

    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 50
    n2 = 200

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

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
