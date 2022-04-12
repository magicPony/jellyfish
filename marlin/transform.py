"""
List of manipulation of candlestick charts
"""
import pandas as pd

from marlin import indicator


def to_heiken_ashi(ohlc: pd.DataFrame,
                   open_col='Open', high_col='High',
                   low_col='Low', close_col='Close'):
    """
    Transform japanese chart to heiken ashi style
    """
    ha_ohlc = indicator.heiken_ashi(ohlc, open_col, high_col, low_col, close_col)
    ohlc[open_col] = ha_ohlc[0]
    ohlc[high_col] = ha_ohlc[1]
    ohlc[low_col] = ha_ohlc[2]
    ohlc[close_col] = ha_ohlc[3]
