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


def tick_bars(ohlc: pd.DataFrame,
              trades_per_candle,
              trades_col=NUM_OF_TRADES,
              agg=None):
    """
    Transform chart to tick bars chart

    Args:
        ohlc: dataframe with candles
        trades_per_candle: number of trader limit per one candle
        trades_col: trades number column name
        agg: candle downsampling aggregation info
    """
    if agg is None:
        agg = DEFAULT_SAMPLING_AGG

    data = []
    i = 0
    progress = trange(len(ohlc))
    while i < len(ohlc):
        j = i + 1
        while j < len(ohlc) and ohlc[trades_col][i:j].sum() < trades_per_candle:
            j += 1

        candle = ohlc.iloc[i:j]
        progress.update(j - i)
        i = j
        data.append(utils.collapse_candle(candle, agg))

    return pd.DataFrame(data, columns=agg.keys())
