"""
List of manipulation of candlestick charts
"""
import numpy as np
import pandas as pd

from jellyfish import indicator


def to_log_prices(ohlc: pd.DataFrame,
                  open_col='Open', high_col='High',
                  low_col='Low', close_col='Close'):
    """
    Apply logarithmic scale to the prices
    Args:
        ohlc: ohlc dataframe
        open_col: open price column name
        high_col: high price column name
        low_col: low price column name
        close_col: close price column name

    Returns:

    """
    for col in [open_col, high_col, low_col, close_col]:
        ohlc[col] = ohlc[col].apply(np.log)


def to_heiken_ashi(ohlc: pd.DataFrame,
                   open_col='Open', high_col='High',
                   low_col='Low', close_col='Close'):
    """
    Transform chart to heiken ashi style chart

    Args:
        ohlc: dataframe with candles
        open_col: open price column name
        high_col: high price column name
        low_col: low price column name
        close_col: closing price column name
    """
    ha_ohlc = indicator.heiken_ashi(ohlc, open_col, high_col, low_col, close_col)
    ohlc[open_col] = ha_ohlc[0]
    ohlc[high_col] = ha_ohlc[1]
    ohlc[low_col] = ha_ohlc[2]
    ohlc[close_col] = ha_ohlc[3]
