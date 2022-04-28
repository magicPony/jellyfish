"""
List of indicators for candlestick charts
"""
from typing import Sized, Iterable

import numpy as np
import pandas as pd
import tulipy as ti
from hurst import compute_Hc
from zigzag import peak_valley_pivots

HURST_RANDOM_WALK = 'random_walk'
HURST_CHANGE = 'change'
HURST_PRICE = 'price'


def _add_nans_prefix(seq: np.ndarray, target_len):
    """
    Add prefix with nan's at the beginning of the sequence
    Args:
        seq: numpy sequence
        target_len: target sequence length

    Returns: sequence with leading nan's
    """
    seq = seq.tolist()
    seq = [None] * (target_len - len(seq)) + seq
    return np.array(seq)


def wad(high, low, close):
    return _add_nans_prefix(ti.wad(np.array(high), np.array(low), np.array(close)), target_len=len(high))


def will_r(high, low, close, period=25):
    return _add_nans_prefix(ti.willr(np.array(high), np.array(low), np.array(close), period), target_len=len(high))


def wilders(signal: Iterable, period):
    return _add_nans_prefix(ti.wilders(np.array(signal), period), target_len=len(signal))


def stoch_rsi(signal: Iterable, period=40):
    return _add_nans_prefix(ti.stochrsi(np.array(signal), period), target_len=len(signal))


def stoch(high, low, close, pct_k_period=5, pct_k_slowing_period=3, pct_d_period=3):
    return [_add_nans_prefix(i, len(high)) for i in ti.stoch(np.array(high), np.array(low), np.array(close), pct_k_period, pct_k_slowing_period, pct_d_period)]


def fisher(high, low, period=25):
    """
    Compute Fisher Transform
    Args:
        high: high values
        low: low values
        period: window size
    """
    res = np.ones((2, len(high))) * np.nan
    high = np.array(high)
    low = np.array(low)
    res[:, period - 1:] = ti.fisher(high, low, period)
    return res


def cmo(signal, period=25):
    """
    Compute Chande Momentum Oscillator
    Args:
        signal: signal sequence
        period: window size
    """
    return _add_nans_prefix(ti.cmo(np.array(signal), period), len(signal))


def bop(opens, high, low, close):
    """
    Balance of Power
    Args:
        opens: open prices sequence
        high: high prices sequence
        low: low prices sequence
        close: close prices sequence
    """
    return ti.bop(np.array(opens), np.array(high), np.array(low), np.array(close))

def dpo(signal, period=25):
    """
    Compute Detrended Price Oscillator
    Args:
        signal: signal sequence
        period: window size
    """
    return _add_nans_prefix(ti.dpo(np.array(signal), period), len(signal))


def kvo(high, low, close, volume, short_period, long_period):
    """
    Compute Klinger Volume Oscillator
    Args:
        high: high prices sequence
        low: low prices sequence
        close: close prices sequence
        volume: volume prices sequence
        short_period: short period
        long_period: long period
    """
    return _add_nans_prefix(ti.kvo(np.array(high), np.array(low), np.array(close), np.array(volume),
                                   short_period, long_period), len(high))


def mass(high, low, period=25):
    """
    Compute Mass Index
    Args:
        high: high prices values
        low: low prices values
        period: window size
    """
    return _add_nans_prefix(ti.mass(np.array(high), np.array(low), period), len(high))


def lag(signal, period=10):
    """
    Shift signal on certain number of ticks
    Args:
        signal: signal sequence
        period: shift period
    """
    return _add_nans_prefix(ti.lag(np.array(signal), period), len(signal))


def macd(signal: Sized, short_period, long_period, signal_period):
    """
    Compute Moving Average Convergence/Divergence
    Args:
        signal: signal sequence
        short_period: fast moving average period
        long_period: slow moving average period
        signal_period: signal period
    """
    res = np.zeros((3, len(signal))) * np.nan
    res[:, long_period-1:] = ti.macd(signal, short_period, long_period, signal_period)
    return res


def sma(signal: Iterable, period):
    """
    Simple moving average indicator calculation
    Args:
        signal: signal sequence
        period:  time window

    Returns: SMA
    """
    return _add_nans_prefix(ti.sma(np.array(signal), period), len(signal))


def aroon(signal_high: Iterable, signal_low: Iterable, period=25):
    """
    Compute aroon momentum indicator
    Args:
        signal_high: signal sequence for highs
        signal_low: signal sequence for lows
        period: period window

    Returns: aroon indicator for highs and lows
    """
    signal_high = np.array(signal_high)
    signal_low = np.array(signal_low)
    res = np.ones((2, signal_high.shape[0])) * np.nan
    res[:, period:] = ti.aroon(signal_high, signal_low, period)
    return res


def ema(signal: Sized, days, smoothing=2):
    """
    Exponential moving average indicator
    Args:
        signal: prices signal
        days: days window
        smoothing: smoothing value

    Returns: EMA sequence
    """
    moving_average = [sum(signal[:days]) / days] * days
    for price in signal[days:]:
        value = price * (smoothing / (1 + days)) + \
                moving_average[-1] * (1 - (smoothing / (1 + days)))
        moving_average.append(value)

    assert len(moving_average) == len(signal)
    return np.array(moving_average)


def bollinger_bands(data: pd.DataFrame, n_lookback, n_std):
    """
    Bollinger bands indicator
    Args:
        data: OHLC dataframe
        n_lookback:lookback ticks number
        n_std: deviation

    Returns: bollinger bands(upper and lower)
    """
    hlc3 = (data.High + data.Low + data.Close) / 3
    mean, std = hlc3.rolling(n_lookback).mean(), hlc3.rolling(n_lookback).std()
    upper = mean + n_std * std
    lower = mean - n_std * std

    lower[:n_lookback] = None
    upper[:n_lookback] = None

    return upper, lower


def aroon_oscillator(signal_high: Iterable = None, signal_low: Iterable = None, period=25):
    """
    Compute aroon oscillator from aroon functions
    Args:
        signal_high: signal sequence for highs
        signal_low: signal sequence for lows
        period: period window

    Returns: aroon oscillator
    """
    ind = aroon(signal_high, signal_low, period)
    return ind[0] - ind[1]


def rsi(signal: Sized, period):
    """
    Relative strength indicator
    Args:
        signal: signal data
        period: period of capturing stats

    Returns: RSI value
    """
    return _add_nans_prefix(ti.rsi(np.array(signal), period), len(signal))


def hurst(signal: Sized, window_size=100, kind=HURST_RANDOM_WALK):
    """
    Compute hurst exponent signal for momentum validation
    Args:
        signal: signal sequence
        window_size: rolling window size
        kind: kind of signal

    Returns: hust exponent
    """
    res = np.ones_like(signal) * 0.5
    for i in range(window_size, len(signal)+1):
        res[i-1], _, _ = compute_Hc(signal[i-window_size:i], simplified=True, kind=kind)

    res[:window_size] = None
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


def heiken_ashi(price_open: np.ndarray,
                price_high: np.ndarray,
                price_low: np.ndarray,
                price_close: np.ndarray):
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
