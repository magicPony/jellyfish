"""
List of possible sampling technics
"""
import pandas as pd
from tqdm import trange


# TODO: join every column of candle instead of major OHLCV
def tick_bars(ohlc: pd.DataFrame,
                 trades_per_candle,
                 open_col='Open', high_col='High',
                 low_col='Low', close_col='Close',
                 volume_col='Volume', trades_col='NumOfTrades'):
    """
    Transform chart to tick bars chart
    More info here: https://towardsdatascience.com/advanced-candlesticks-for-machine-learning-i-tick-bars-a8b93728b4c5

    Args:
        ohlc: dataframe with candles
        trades_per_candle: number of trader limit per one candle
        open_col: open price column name
        high_col: high price column name
        low_col: low price column name
        close_col: closing price column name
        volume_col: volume column name
        trades_col: trades number column name
    """
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    trades = []
    indices = []

    i = 0
    progress = trange(len(ohlc))
    while i < len(ohlc):
        j = i + 1
        while j < len(ohlc) and ohlc[trades_col][i:j].sum() < trades_per_candle:
            j += 1

        candle = ohlc.iloc[i:j]
        progress.update(j - i)
        i = j

        opens.append(candle[open_col][0])
        highs.append(candle[high_col].max())
        lows.append(candle[low_col].min())
        closes.append(candle[close_col][-1])
        volumes.append(candle[volume_col].sum())
        trades.append(candle[trades_col].sum())
        indices.append(candle.index[-1])

    return pd.DataFrame({
        open_col: opens,
        high_col: highs,
        low_col: lows,
        close_col: closes,
        volume_col: volumes,
        trades_col: trades
    }, index=indices)
