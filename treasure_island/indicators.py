import numpy as np
import pandas as pd


def heiken_ashi(
        ohlc: pd.DataFrame,
        open_col='Open',
        high_col='High',
        low_col='Low',
        close_col='Close'):
    ha_open = []
    ha_high = []
    ha_low = []
    ha_close = []
    for _, row in ohlc.iterrows():
        open, high, low, close = row[open_col], row[high_col], row[low_col], row[close_col]
        if len(ha_open) == 0:
            ha_open.append(open)
            ha_high.append(high)
            ha_low.append(low)
            ha_close.append(close)
            continue

        ha_open.append((ha_open[-1] + ha_close[-1]) / 2)
        ha_close.append((open + high + low + close) / 4)
        ha_low.append(min(low, ha_open[-1], ha_close[-1]))
        ha_high.append(max(high, ha_open[-1], ha_close[-1]))

    return np.array(ha_open), np.array(ha_high), np.array(ha_low), np.array(ha_close)
