from datetime import datetime

import numpy as np
import pandas as pd

from jellyfish import indicator
from jellyfish import utils
from jellyfish.core import Client
from jellyfish.core import SmaCross, Backtest
from jellyfish.history_loader import load_candles_history
from jellyfish.transform.sampling import _generic_sampling, DEFAULT_SAMPLING_AGG
from jellyfish.constants import DATE

th = None
th_eps = None


def preprocess(frame: pd.DataFrame):
    returns = frame.Close / frame.Open
    hurst = indicator.hurst(returns, kind=indicator.HURST_CHANGE, simplified=False)

    global th
    global th_eps
    if th is None:
        th = hurst[100:].mean()
        th_eps = hurst[100:].std() * 3.5e-1

    frame['Persistent'] = (hurst > th + th_eps).astype(np.int32)
    frame['Reversal'] = (hurst < th - th_eps).astype(np.int32)
    frame['RandomWalk'] = (np.abs(hurst - th) < th_eps).astype(np.int32)
    frame['i_Hurst'] = hurst
    return frame


def main():
    utils.disable_warnings()

    pair = 'btcusdt'
    size = 5000 * 2
    mid_dt = datetime(year=2021, month=9, day=25)

    frame = load_candles_history(Client(), pair, end_dt=mid_dt, interval='1m', candles_num=size)
    val_frame = load_candles_history(Client(), pair, start_dt=mid_dt, interval='1m',
                                     candles_num=size)

    frame = preprocess(frame)
    val_frame = preprocess(val_frame)

    condition = lambda ohlc: ohlc.Persistent.max() + ohlc.Reversal.max() > 1
    frame = _generic_sampling(frame.reset_index(), condition, DEFAULT_SAMPLING_AGG).set_index(DATE)
    val_frame = _generic_sampling(val_frame.reset_index(), condition, DEFAULT_SAMPLING_AGG).set_index(
        DATE)

    bt = Backtest(frame, SmaCross, trade_on_close=True)
    stats = bt.optimize(
        n1=range(5, 25, 2),
        n2=range(5, 25, 2),
        constraint=lambda p: p.n1 < p.n2,
        maximize='Calmar Ratio',
    )

    params = stats._strategy
    bt = Backtest(val_frame, SmaCross, trade_on_close=True)
    stats = bt.run(
        n1=params.n1,
        n2=params.n2
    )
    bt.plot(open_browser=True)
    print(stats)


if __name__ == '__main__':
    main()
