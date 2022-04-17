"""
List of possible sampling technics
"""
import pandas as pd
import stocktrends
from tqdm import trange
from zigzag import peak_valley_pivots

import jellyfish.transform.sampling_triggers as triggers
from jellyfish import utils
from jellyfish.constants import (OPEN, HIGH, LOW, CLOSE, VOLUME, DATE,
                                 NUM_OF_TRADES, QUOTE_ASSET_VOLUME)

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


def _generic_sampling(ohlc: pd.DataFrame, condition_cb, agg: dict = None):
    """
    Generic sampling backbone
    Args:
        ohlc: dataframe with candles
        condition_cb: sampling condition callback
        agg: candle downsampling aggregation info

    Returns: downsampled data
    """
    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

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


def tick_imbalance(ohlc: pd.DataFrame,
                   imbalance,
                   close_col=CLOSE,
                   agg: dict = None):
    """
    Transform initial chart to line break

    Args:
        ohlc: dataframe with candles
        imbalance: tick imbalance threshold
        close_col: close column name
        agg: candle downsampling aggregation info

    Returns: downsampled data
    """
    condition = triggers.tick_imbalance(close_col, imbalance)
    return _generic_sampling(ohlc, condition, agg)


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
    condition = triggers.line_break(close_col, lookback)
    return _generic_sampling(ohlc, condition, agg)


def zigzag(ohlc: pd.DataFrame,
           threshold,
           prices_col=CLOSE,
           agg: dict = None):
    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

    pivots = peak_valley_pivots(ohlc[prices_col].to_numpy(), threshold, -threshold)
    pivot_idx = [i for i, state in enumerate(pivots) if state != 0]
    data = []
    for start, fin in zip(pivot_idx[:-1], pivot_idx[1:]):
        data.append(utils.collapse_candle(ohlc[start:fin], agg))

    return pd.DataFrame(data, columns=agg.keys())


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
    condition = triggers.apply_column_greater(trades_col, 'sum', trades_per_candle)
    return _generic_sampling(ohlc, condition, agg)


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
    condition = triggers.apply_column_greater(volume_col, 'sum', volume_per_candle)
    return _generic_sampling(ohlc, condition, agg)


def dollar_bars(ohlc: pd.DataFrame,
                dollars_per_candle,
                dollars_col=QUOTE_ASSET_VOLUME,
                agg: dict = None):
    """
    Transform chart to dollar bars

    Args:
        ohlc: dataframe with candles
        dollars_per_candle: dollars volume per one candle
        dollars_col: dollars volume column name
        agg: candle downsampling aggregation info

    Returns: downsampled data
    """
    condition = triggers.apply_column_greater(dollars_col, 'sum', dollars_per_candle)
    return _generic_sampling(ohlc, condition, agg)


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

    renko = stocktrends.indicators.Renko(ohlc)
    renko.brick_size = brick_size
    renko.chart_type = stocktrends.indicators.Renko.PERIOD_CLOSE
    ohlc = renko.get_ohlc_data()

    reversed_rename_map = {v: k for k, v in rename_map.items()}
    ohlc.columns = rename(ohlc.columns, reversed_rename_map)

    return ohlc
