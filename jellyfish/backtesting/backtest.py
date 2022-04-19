"""
Backtesting.py Backtest module wrapper
"""
import backtesting

from jellyfish import CACHE_PATH


class Backtest(backtesting.Backtest):
    """
    Wrapper for Backtest
    """

    def plot(self, *, filename=None, show_legend=True, open_browser=True, **kwargs):
        """
        Plot the progression of the last backtest run.

        Args:
            filename: path to save the interactive HTML plot to
            show_legend: if `True`, the resulting plot graphs will contain labeled legends
            open_browser: if `True`, the resulting `filename` will be opened in the default
                          web browser
        """
        if filename is None:
            filename = (CACHE_PATH / 'test.html').as_posix()

        assert len(kwargs) == 0
        backtesting.Backtest.plot(self, filename=filename, show_legend=show_legend,
                                  open_browser=open_browser)
