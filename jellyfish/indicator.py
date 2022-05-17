"""
List of indicators for candlestick charts
"""
from typing import Sized, Iterable

import numpy as np
import pandas as pd
import scipy.signal as scp_signal
import tulipy as ti
from hurst import compute_Hc
from scipy import stats

HURST_RANDOM_WALK = 'random_walk'
HURST_CHANGE = 'change'
HURST_PRICE = 'price'


def volume_profile_valleys(prices: np.ndarray, volumes: np.ndarray, bins_num):
    """
    Volume profile valley points
    Args:
        prices: prices data
        volumes: volumes data
        bins_num: number of valley (actual number would be lower!)

    Returns: valley prices
    """
    # pylint: disable=invalid-name
    price_range = prices.min(), prices.max()

    kde_factor = 2e-2
    kde = stats.gaussian_kde(prices, weights=volumes, bw_method=kde_factor)
    xr = np.linspace(*price_range, bins_num)
    kdy = kde(xr)

    lows, _ = scp_signal.find_peaks(1 - kdy)

    pkx = xr[lows]

    return pkx


def volume_profile(prices: Iterable,
                   volumes: Iterable,
                   bins=None):
    """
    Volume profile horizontal indicator
    Args:
        prices: prices
        volumes: volumes
        bins: bins ranges

    Returns: hist volume profile
    """
    profile = np.zeros(len(bins))
    assert bins is not None
    bin_idx = 0
    for price, vol in zip(prices, volumes):
        while bins[bin_idx] < price:
            bin_idx += 1

        while bin_idx > 0 and bins[bin_idx - 1] >= price:
            bin_idx -= 1

        profile[bin_idx] += vol

    return profile


def fib_retracement(high: np.ndarray, low: np.ndarray):
    ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    max_level = high.max()
    min_level = low.min()
    is_up_direction = low.argmin() < high.argmax()

    levels = []
    for ratio in ratios:
        if is_up_direction:  # Uptrend
            levels.append(max_level - (max_level - min_level) * ratio)
        else:  # Downtrend
            levels.append(min_level + (max_level - min_level) * ratio)

    return levels


def marketfi(high, low, volume):
    """
    Market Facilitation Index
    Args:
        high: high prices
        low: low prices
        volume: volumes

    Returns: index signal
    """
    return _add_nans_prefix(ti.marketfi(np.array(high), np.array(low), np.array(volume)), len(high))


def mfi(high, low, close, volume, period):
    """
    Money flow index
    Args:
        high: high prices
        low: low prices
        close: close prices
        volume: volumes
        period: period

    Returns: mfi signal
    """
    return _add_nans_prefix(ti.mfi(np.array(high), np.array(low), np.array(close), np.array(volume),
                                   period), len(high))


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
    """
    Compute Williams Accumulation/Distribution
    Args:
        high: high price values
        low: low price values
        close: close price values
    """
    return _add_nans_prefix(ti.wad(np.array(high), np.array(low), np.array(close)), len(high))


def will_r(high, low, close, period=25):
    """
    Compute Williams %R
    Args:
        high: high price values
        low: low price values
        close: close price values
        period: rolling window size
    """
    return _add_nans_prefix(ti.willr(np.array(high), np.array(low), np.array(close), period),
                            target_len=len(high))


def wilders(signal: Iterable, period):
    """
    Compute Wilders Smoothing
    Args:
        signal: values sequence
        period: rolling window size
    """
    return _add_nans_prefix(ti.wilders(np.array(signal), period), target_len=len(signal))


def stoch_rsi(signal: Iterable, period=40):
    """
    Compute Stochastic RSI
    Args:
        signal: values sequence
        period: rolling window size
    """
    return _add_nans_prefix(ti.stochrsi(np.array(signal), period), target_len=len(signal))


def stoch(high, low, close, pct_k_period=5, pct_k_slowing_period=3, pct_d_period=3):
    """
    Compute Stochastic Oscillator
    Args:
        high: high price values
        low: low price values
        close: close price values
        pct_k_period: %k period
        pct_k_slowing_period: %k slowing period
        pct_d_period: %d period
    """
    ind = ti.stoch(np.array(high), np.array(low), np.array(close),
                   pct_k_period, pct_k_slowing_period, pct_d_period)
    return [_add_nans_prefix(i, len(high)) for i in ind]


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
    res[:, long_period - 1:] = ti.macd(np.array(signal), short_period, long_period, signal_period)
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

    return lower, upper


def dumb_sr_lines(high, low, n_lookback=20, low_extreme=0.1, high_extreme=0.1):
    """
    Compute Support/Resistance lines
    Args:
        high: high price values
        low: low price values
        n_lookback: lookback ticks number
        low_extreme: support line high-low range weight
        high_extreme: resistance line high-low range weight
    """
    rolling = lambda data, cb: np.array([cb(data[i - n_lookback:i + 1])
                                         for i in range(n_lookback, len(data))])
    rlng_high = rolling(high, np.max)
    rlng_low = rolling(low, np.min)
    rlng_range = rlng_high - rlng_low
    support = _add_nans_prefix(rlng_low + rlng_range * low_extreme, len(high))
    resistance = _add_nans_prefix(rlng_high - rlng_range * high_extreme, len(high))
    return support, resistance


def awesome(high, low, fast_period=5, slow_period=34):
    """
    Compute Awesome Oscillator
    Args:
        high: signal sequence for highs
        low: signal sequence for lows
        fast_period: fast SMA period
        slow_period: slow SMA period
    """
    midprice = (np.array(high) + np.array(low)) / 2
    fast_ma = ti.sma(np.array(midprice), fast_period)[slow_period - fast_period:]
    slow_ma = ti.sma(np.array(midprice), slow_period)
    return _add_nans_prefix(fast_ma - slow_ma, len(high))


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
    for i in range(window_size, len(signal) + 1):
        res[i - 1], _, _ = compute_Hc(signal[i - window_size:i], simplified=True, kind=kind)

    res[:window_size] = None
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
