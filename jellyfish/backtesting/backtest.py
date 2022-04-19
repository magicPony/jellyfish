"""
Backtesting.py Backtest module wrapper
"""
import backtesting

from jellyfish import CACHE_PATH


class Backtest(backtesting.Backtest):
    """
    Wrapper for Backtest
    """

    def plot(self, *, results=None, filename=None, plot_width=None, plot_equity=True,
             plot_return=False, plot_pl=True, plot_volume=True, plot_drawdown=False,
             smooth_equity=False, relative_equity=True, superimpose=True, show_legend=True,
             open_browser=True, **kwargs):
        """
        Plot the progression of the last backtest run.

        Args:
            results: if provided, it should be a particular result `pd.Series` such as returned by
                    `backtesting.backtesting.Backtest.run` or, otherwise the last  run's results
                    are used.
            filename: path to save the interactive HTML plot to
            plot_width: the width of the plot in pixels
            plot_equity: if `True`, the resulting plot will contain an equity graph section
            plot_return: if `True`, the resulting plot will contain cumulative return price section
            plot_pl: if `True`, the resulting plot will contain a profit/loss (P/L)
                     indicator section
            plot_volume: if `True`, the resulting plot will contain a trade volume section
            plot_drawdown: if `True`, the resulting plot will contain a separate drawdown
                           graph section
            smooth_equity: the equity graph will be interpolated between fixed points at trade
                           closing times
            relative_equity: if `True`, scale and label equity graph axis with return percent,
                             not absolute cash-equivalent values
            superimpose: if `True`, superimpose larger-timeframe candlesticks over the original
                         candlestick chart
            show_legend: if `True`, the resulting plot graphs will contain labeled legends
            open_browser: if `True`, the resulting `filename` will be opened in the default
                          web browser
        """
        if filename is None:
            filename = (CACHE_PATH / 'test.html').as_posix()

        assert len(kwargs) == 0
        backtesting.Backtest.plot(self, filename=filename, results=results, plot_width=plot_width,
                                  plot_equity=plot_equity, plot_return=plot_return, plot_pl=plot_pl,
                                  plot_volume=plot_volume, plot_drawdown=plot_drawdown,
                                  smooth_equity=smooth_equity, relative_equity=relative_equity,
                                  superimpose=superimpose, show_legend=show_legend,
                                  open_browser=open_browser)
