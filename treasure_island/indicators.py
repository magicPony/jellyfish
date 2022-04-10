import numpy as np
import pandas as pd


def heiken_ashi(
        ohlc: pd.DataFrame,
        open_col='Open',
        high_col='High',
        low_col='Low',
        close_col='Close'):
    ha_ohlc = []
    for _, row in ohlc.iterrows():
        open, high, low, close = row[open_col], row[high_col], row[low_col], row[close_col]
        if len(ha_ohlc) == 0:
            ha_ohlc.append([open, high, low, close])
            continue

        ha_open = (ha_ohlc[-1][0] + ha_ohlc[-1][3]) / 2
        ha_close = (open + high + low + close) / 4
        ha_low = min(low, ha_open, ha_close)
        ha_high = max(high, ha_open, ha_close)
        ha_ohlc.append([ha_open, ha_high, ha_low, ha_close])

    ha_ohlc = np.array(ha_ohlc)
    return ha_ohlc.transpose()
