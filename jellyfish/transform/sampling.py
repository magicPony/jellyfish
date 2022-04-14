"""
List of possible sampling technics
"""
import pandas as pd
from tqdm import trange
from stocktrends import indicators

from jellyfish import utils
from jellyfish.constants import (OPEN, HIGH, LOW, CLOSE, VOLUME, DATE, NUM_OF_TRADES)

DEFAULT_SAMPLING_AGG_WITHOUT_IDX = {
    OPEN: utils.first,
    HIGH: 'max',
    LOW: 'min',
    CLOSE: utils.last,
    VOLUME: 'sum'
}

DEFAULT_SAMPLING_AGG = {
    **DEFAULT_SAMPLING_AGG_WITHOUT_IDX,
    DATE: utils.last
}


def _generic_sampling(ohlc: pd.DataFrame, agg: dict, condition_cb):
    """
    Generic sampling backbone
    Args:
        ohlc: dataframe with candles
        agg: candle downsampling aggregation info
        condition_cb: sampling condition callback

    Returns: downsampled data
    """
    data = []
    i = 0
    progress = trange(len(ohlc))
    while i < len(ohlc):
        j = i + 1
        while j < len(ohlc) and not condition_cb(ohlc[i:j]):
            j += 1

        data.append(utils.collapse_candle(ohlc[i:j], agg))
        progress.update(j - i)
        i = j

    return pd.DataFrame(data, columns=agg.keys())


def line_break_bars(ohlc: pd.DataFrame,
                    lookback: int = 3,
                    close_col=CLOSE,
                    agg: dict = None):
    """
    Transform initial chart to line break

    Args:
        ohlc: dataframe with candles
        lookback: number of 'lookback' candles
        close_col: close column name
        agg: candle downsampling aggregation info

    Returns: downsampled data
    """
    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

    def condition(ohlc_sample: pd.DataFrame):
        sample_size = len(ohlc_sample)
        if sample_size <= lookback:
            return False

        prices = list(ohlc_sample[close_col])[-lookback:]
        return max(prices) <= prices[-1] or min(prices) >= prices[-1]

    return _generic_sampling(ohlc, agg, condition)


def tick_bars(ohlc: pd.DataFrame,
              trades_per_candle,
              trades_col=NUM_OF_TRADES,
              agg: dict = None):
    """
    Transform chart to tick bars chart

    Args:
        ohlc: dataframe with candles
        trades_per_candle: number of trader limit per one candle
        trades_col: trades number column name
        agg: candle downsampling aggregation info

    Returns: downsampled data
    """
    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

    def condition(ohlc_sample: pd.DataFrame):
        return ohlc_sample[trades_col].sum() >= trades_per_candle

    return _generic_sampling(ohlc, agg, condition)


def volume_bars(ohlc: pd.DataFrame,
                volume_per_candle,
                volume_col=VOLUME,
                agg: dict = None):
    """
    Transform chart to volume bars chart

    Args:
        ohlc: dataframe with candles
        volume_per_candle: volume per one candle
        volume_col: volume column name
        agg: candle downsampling aggregation info

    Returns: downsampled data
    """
    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

    def condition(ohlc_sample: pd.DataFrame):
        return ohlc_sample[volume_col].sum() >= volume_per_candle

    return _generic_sampling(ohlc, agg, condition)


def renko_bars(ohlc: pd.DataFrame,
               brick_size=2,
               open_col=OPEN,
               high_col=HIGH,
               low_col=LOW,
               close_col=CLOSE,
               volume_col=VOLUME,
               date_col=DATE):
    """
    Transform chart to renko

    Args:
        ohlc: dataframe with candles
        brick_size: renko brick size
        open_col: open column name
        high_col: high column name
        low_col: low column name
        close_col: close column name
        volume_col: volume column name
        date_col: date column name

    Returns: renko chart
    """
    def rename(columns: pd.Index, rename_map: dict):
        res = list(range(len(columns)))
        for i, name in enumerate(columns):
            if name in rename_map and rename_map[name] is not None:
                res[i] = rename_map[name]

        return res

    rename_map = {
        open_col: OPEN.lower(),
        high_col: HIGH.lower(),
        low_col: LOW.lower(),
        close_col: CLOSE.lower(),
        volume_col: VOLUME.lower(),
        date_col: DATE.lower()
    }

    ohlc.columns = rename(ohlc.columns, rename_map)

    renko = indicators.Renko(ohlc)
    renko.brick_size = brick_size
    renko.chart_type = indicators.Renko.PERIOD_CLOSE
    ohlc = renko.get_ohlc_data()

    reversed_rename_map = {v: k for k, v in rename_map.items()}
    ohlc.columns = rename(ohlc.columns, reversed_rename_map)

    return ohlc
