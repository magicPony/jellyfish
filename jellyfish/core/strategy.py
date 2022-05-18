"""
Backtesting.py Strategy module wrapper
"""
import backtesting
import numpy as np
from backtesting.lib import crossover
from backtesting.test import SMA


class Strategy(backtesting.Strategy):
    """
    Dummy empty strategy
    """
    def init(self):
        for col in self.data.df.columns:
            try:
                if col.startswith('i_'):
                    self.mark_as_indicator(col)
            except AttributeError:
                pass

    def next(self):
        pass

    def plot_hline(self, price, force=False, name=None, color=None):
        """
        Plot vertical line
        Args:
            price: price level
            force: force plot when y level is out of price range
            name: line name
            color: line plot color

        """
        to_hline = lambda lvl: np.ones_like(self.data.Close) * lvl
        if force or self.data.Low.min() <= price <= self.data.High.max():
            self.I(to_hline, price, name=name, color=color)

    def mark_as_indicator(self, column_name, overlay=None, name=None, scatter=False):
        """
        Mark dataframe column as an indicator
        Args:
            column_name: dataframe column namae
            overlay: plot indicator overlay candles chart
            name: indicator name
            scatter: plot circles instead of connected line segments

        Returns: indicator
        """
        name = name or column_name
        display_name = name[2:] if name.startswith('i_') else name
        return self.I(lambda x: x, self.data.df[column_name],
                      name=display_name, overlay=overlay, scatter=scatter)


class BuyAndHold(Strategy):
    """
    Simple buy&hold strategy
    """
    def next(self):
        if len(self.trades) == 0:
            self.buy()


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
        Strategy.init(self)

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
