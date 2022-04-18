"""
List of indicators for candlestick charts
"""
import numpy as np
from zigzag import peak_valley_pivots
from hurst import compute_Hc


def hurst(signal: np.ndarray, window_size, kind='random_walk'):
    """
    Compute hurst exponent signal for momentum validation
    Args:
        signal: signal sequence
        window_size: rolling window size
        kind: kind of signal

    Returns: hust exponent
    """
    res = np.zeros_like(signal)
    for i in range(window_size, len(signal)):
        res[i-1], _, _ = compute_Hc(signal[i-window_size:i], simplified=True, kind=kind)

    res[0:window_size-2] = res[window_size-1]
    return res


def zigzag(prices: np.ndarray, threshold):
    """
    ZigZag indicator

    Args:
        prices: prices list
        threshold: relative change threshold

    Returns: zigzag prices
    """
    pivots = peak_valley_pivots(prices, threshold, -threshold)
    pivot_idx = [i for i, state in enumerate(pivots) if state != 0]
    res = np.zeros_like(prices)
    for start, fin in zip(pivot_idx[:-1], pivot_idx[1:]):
        p_start = prices[start]
        p_fin = prices[fin]
        size = fin-start+1
        res[start:fin + 1] = np.arange(p_start, p_fin,
                                       (p_fin - p_start) / (fin - start + 1))[:size]

    return res


def heiken_ashi(price_open,
                price_high,
                price_low,
                price_close):
    """
    Hieken ashi candle prices
    Args:
        price_open: open price
        price_high: close price
        price_low: low price
        price_close: close [rice

    Returns: heiken ashi candle prices
    """
    ha_open = []
    ha_high = []
    ha_low = []
    ha_close = []
    for open_, high, low, close in zip(price_open, price_high, price_low, price_close):
        if len(ha_open) == 0:
            ha_open.append(open_)
            ha_high.append(high)
            ha_low.append(low)
            ha_close.append(close)
            continue

        ha_open.append((ha_open[-1] + ha_close[-1]) / 2)
        ha_close.append((open_ + high + low + close) / 4)
        ha_low.append(min(low, ha_open[-1], ha_close[-1]))
        ha_high.append(max(high, ha_open[-1], ha_close[-1]))

    return np.array(ha_open), np.array(ha_high), np.array(ha_low), np.array(ha_close)
