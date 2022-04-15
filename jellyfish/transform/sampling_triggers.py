"""
Sampling triggers factory
"""
import pandas as pd


def line_break(close_col, lookback):
    """
    Line break chart trigger callback
    Args:
        close_col: close column name
        lookback: number of 'lookback' candles

    Returns: trigger callable
    """
    def condition(ohlc: pd.DataFrame):
        sample_size = len(ohlc)
        if sample_size <= lookback:
            return False

        prices = list(ohlc[close_col])[-lookback:]
        return max(prices) <= prices[-1] or min(prices) >= prices[-1]

    return condition


def apply_column_greater(column_name, func, thr):
    """
    Generic "apply and compare" trigger callback
    Args:
        column_name: column name
        func: function to apply for column
        thr: comparable threshold value

    Returns: trigger value
    """
    return lambda ohlc: ohlc[column_name].apply(func) > thr


def apply_column_less(column_name, func, thr):
    """
    Generic "apply and compare" trigger callback
    Args:
        column_name: column name
        func: function to apply for column
        thr: comparable threshold value

    Returns: trigger value
    """
    return lambda ohlc: ohlc[column_name].apply(func) < thr
