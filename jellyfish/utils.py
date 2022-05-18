"""
Utility functions
"""
import warnings

import pandas as pd

from jellyfish.core import Strategy, Backtest


def plot_ohlc(ohlc: pd.DataFrame, open_browser=True, show_legend=True):
    """
    Plot OHLC chart from dataframe
    Args:
        ohlc: dataframe
        open_browser: open html report in browser
        show_legend: show equity/pnl legend
    """
    backtest = Backtest(ohlc, strategy=Strategy)
    backtest.run()
    backtest.plot(open_browser=open_browser, show_legend=show_legend)


def disable_warnings():
    """
    Disables all warnings
    """
    warnings.filterwarnings("ignore")


def collapse_candle(data: pd.DataFrame, agg: dict):
    """
    Downsample OHLC candle
    Args:
        data: OHLC frame
        agg: aggregation dict

    Returns: frame with aggregated result
    """
    return [data[col].agg(func) for col, func in agg.items()]
