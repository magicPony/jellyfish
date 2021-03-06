"""
List of possible sampling technics
"""
import pandas as pd
import stocktrends
from tqdm.auto import trange

import jellyfish.transform.sampling_triggers as triggers
from jellyfish.constants import (OPEN, HIGH, LOW, CLOSE, VOLUME, DATE, NUM_OF_TRADES,
                                 QUOTE_ASSET_VOLUME, TAKER_SELL_ASSET_VOLUME,
                                 TAKER_BUY_ASSET_VOLUME, ORDERBOOK)


def _first(sequence):
    """
    Get first non null element from the list
    Args:
        sequence: values sequence

    Returns: first non null element from the sequence
    """
    sequence = list(sequence)
    i = 0
    while i + 1 < len(sequence) and sequence[i] is None:
        i += 1

    return sequence[i]


def _last(sequence):
    """
    Get last non null element from the list
    Args:
        sequence: values sequence

    Returns: last non null element
    """
    return _first(list(sequence)[::-1])


DEFAULT_SAMPLING_AGG_WITHOUT_IDX = {
    OPEN: _first,
    HIGH: 'max',
    LOW: 'min',
    CLOSE: _last,
    VOLUME: 'sum',
    NUM_OF_TRADES: 'sum',
    QUOTE_ASSET_VOLUME: 'sum',
    TAKER_BUY_ASSET_VOLUME: 'sum',
    TAKER_SELL_ASSET_VOLUME: 'sum',
    ORDERBOOK: _last
}

DEFAULT_SAMPLING_AGG = {
    **DEFAULT_SAMPLING_AGG_WITHOUT_IDX,
    DATE: _last
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
    if ohlc.index.name == DATE:
        ohlc.reset_index(inplace=True)

    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

    agg = {k: v for k, v in agg.items() if k in ohlc.columns}
    for col in ohlc.columns:
        if col not in agg.keys():
            agg[col] = _last

    data = []
    i = 0
    progress = trange(len(ohlc))
    while i < len(ohlc):
        j = i + 1
        while j < len(ohlc) and not condition_cb(ohlc[i:j]):
            j += 1

        data.append(ohlc[i:j].agg(agg))
        progress.update(j - i)
        i = j

    ohlc = pd.DataFrame(data)
    if DATE in ohlc.columns:
        ohlc.set_index(DATE, inplace=True)

    return ohlc


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
    if ohlc.index.name == DATE:
        ohlc.reset_index(inplace=True)

    def rename(columns: pd.Index, rename_map: dict):
        res = list(range(len(columns)))
        for i, name in enumerate(columns):
            if name in rename_map and rename_map[name] is not None:
                res[i] = rename_map[name]

        return res

    volume_df = ohlc[[date_col, volume_col]].copy()

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
    volumes = [volume_df[volume_df[date_col] <= ohlc[date_col][0]][volume_col]]
    for i in range(1, len(ohlc)):
        from_date = ohlc[date_col][i-1]
        to_date = ohlc[date_col][i]
        volumes.append(volume_df[
                           (from_date < volume_df[date_col]) & (volume_df[date_col] <= to_date)
                           ][volume_col].sum())

    ohlc[volume_col] = volumes
    if DATE in ohlc.columns:
        ohlc.set_index(DATE, inplace=True)

    return ohlc
