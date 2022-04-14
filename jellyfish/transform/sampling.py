"""
List of possible sampling technics
"""
import pandas as pd
from tqdm import trange

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
