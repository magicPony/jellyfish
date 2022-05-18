"""
Backtesting.py Backtest module wrapper
"""
from datetime import timedelta

import backtesting
import numpy as np
import pandas as pd

from jellyfish.constants import CACHE_PATH, DATE


def _get_ticks_per_year(ohlc: pd.DataFrame):
    """
    Calculate average ticks per year
    Args:
        ohlc: dataframe

    Returns: ticks per year
    """
    if DATE in ohlc.columns:
        dates = ohlc[DATE]
    elif isinstance(ohlc.index, pd.DatetimeIndex):
        dates = ohlc.index
    else:
        return None

    dates = dates.tolist()
    years = (dates[-1] - dates[0]) / timedelta(days=365)
    return len(ohlc) / years


class Backtest(backtesting.Backtest):
    """
    Wrapper for Backtest
    """
    FUTURES_MAKER_COMMISSION = 0.0004

    def __init__(self, data: pd.DataFrame,
                 strategy,
                 *,
                 cash: float = 1_000_000,
                 commission=FUTURES_MAKER_COMMISSION,  # e.g. 0.04% for "maker" orders on Binance
                 margin: float = 1.,
                 trade_on_close=False):
        backtesting.Backtest.__init__(self, data=data, strategy=strategy,
                                      cash=cash, commission=commission,
                                      margin=margin, trade_on_close=trade_on_close)

    def plot(self, *, filename=None, show_legend=True, open_browser=False, plot_volume=True,
             **kwargs):
        """
        Plot the progression of the last backtest run.

        Args:
            filename: path to save the interactive HTML plot to
            show_legend: if `True`, the resulting plot graphs will contain labeled legends
            open_browser: if `True`, the resulting `filename` will be opened in the default
                          web browser
            plot_volume: If `plot_volume` is `True`, the resulting plot will contain
                         a trade volume section.
        """
        if filename is None:
            filename = (CACHE_PATH / 'test.html').as_posix()

        assert len(kwargs) == 0
        backtesting.Backtest.plot(self, filename=filename, show_legend=show_legend,
                                  open_browser=open_browser, plot_volume=plot_volume,
                                  superimpose=False)

    def run(self, **kwargs) -> pd.Series:
        """
        Run the backtest. Returns `pd.Series` with results and statistics.
        Compared with inner backtesting engine also computes additional field of stats
        """
        stats = backtesting.Backtest.run(self, **kwargs)
        equity = stats['_equity_curve']
        equity, drawdown = equity['Equity'], equity['DrawdownPct']
        returns = equity.pct_change(1)

        tpy = _get_ticks_per_year(self._data)
        rf_rate = 0  # TODO: replace risk-free rate with an appropriate value
        if returns.std() != 0:
            stats['Sharpe Ratio'] = (returns.mean() * (tpy ** 0.5) - rf_rate) / returns.std()
            stats['Calmar Ratio'] = returns.mean() * tpy / drawdown.max()

        if returns[returns < 0].std() != 0:
            stats['Sortino Ratio'] = (returns.mean() * np.sqrt(tpy) - rf_rate) \
                                     / returns[returns < 0].std()

        return stats
