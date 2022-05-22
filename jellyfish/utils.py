"""
Utility functions
"""
import warnings

import pandas as pd

from jellyfish.core import Strategy, Backtest


def plot_ohlc(ohlc: pd.DataFrame, open_browser=False, show_legend=True, plot_volume=True):
    """
    Plot OHLC chart from dataframe
    Args:
        ohlc: dataframe
        open_browser: open html report in browser
        show_legend: show equity/pnl legend
        plot_volume: plot volume chart
    """
    backtest = Backtest(ohlc, strategy=Strategy)
    backtest.run()
    return backtest.plot(open_browser=open_browser, show_legend=show_legend,
                         plot_volume=plot_volume)


def disable_warnings():
    """
    Disables all warnings
    """
    warnings.filterwarnings("ignore")
