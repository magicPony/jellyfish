"""
Backtesting.py Strategy module wrapper
"""
import backtesting


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
        display_name = name[2:] if name.startswith('i_') else name
        self.I(lambda x: x, self.data.df[column_name],
               name=display_name, overlay=overlay, scatter=scatter)
