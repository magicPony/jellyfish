"""
List of manipulation of candlestick charts
"""
import numpy as np
import pandas as pd

from jellyfish import indicator
from jellyfish.constants import OPEN, HIGH, LOW, CLOSE


def to_log_prices(ohlc: pd.DataFrame,
                  open_col=OPEN, high_col=HIGH,
                  low_col=LOW, close_col=CLOSE):
    """
    Apply logarithmic scale to the prices
    Args:
        ohlc: ohlc dataframe
        open_col: open price column name
        high_col: high price column name
        low_col: low price column name
        close_col: close price column name
    """
    for col in [open_col, high_col, low_col, close_col]:
        ohlc[col] = ohlc[col].apply(np.log)

    return ohlc


def to_heiken_ashi(ohlc: pd.DataFrame,
                   open_col=OPEN, high_col=HIGH,
                   low_col=LOW, close_col=CLOSE):
    """
    Transform chart to heiken ashi style chart

    Args:
        ohlc: dataframe with candles
        open_col: open price column name
        high_col: high price column name
        low_col: low price column name
        close_col: closing price column name
    """
    ha_ohlc = indicator.heiken_ashi(ohlc[open_col], ohlc[high_col], ohlc[low_col], ohlc[close_col])
    ohlc[open_col] = ha_ohlc[0]
    ohlc[high_col] = ha_ohlc[1]
    ohlc[low_col] = ha_ohlc[2]
    ohlc[close_col] = ha_ohlc[3]
    return ohlc


def compose(transforms):
    """
    Create a callback with composed transforms apply
    Args:
        transforms: transforms list

    Returns: application callback
    """
    def ret(ohlc: pd.DataFrame):
        for transform_item in transforms:
            if isinstance(transform_item, tuple):
                ohlc = transform_item[0](ohlc, *transform_item[1:])
            else:
                ohlc = transform_item(ohlc)

        return ohlc

    return ret
