"""
Strategies list
"""

import backtesting


class Strategy(backtesting.Strategy):
    """
    Dummy empty strategy
    """
    def init(self):
        pass

    def next(self):
        pass

    def mark_as_indicator(self, column_name, overlay=None, name=None, scatter=False):
        """
        Mark dataframe column as an indicator
        Args:
            column_name: dataframe column namae
            overlay: plot indicator overlay candles chart
            name: indicator name
            scatter: plot circles instead of connected line segments
        """
        name = name or column_name
        self.I(lambda x: x, self.data.df[column_name], name=name, overlay=overlay, scatter=scatter)
