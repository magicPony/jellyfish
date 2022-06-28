"""
Orderbook history data loading module
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from jellyfish.constants import ORDERBOOK_PATH, DATE, ORDERBOOK

BIDS = 'bids'
ASKS = 'asks'


def _read_orderbook(path: Path):
    """
    Read orderbook from path
    Args:
        path: path to json with orderbook data

    Returns: orderbook numpy array
    """
    if path.exists():
        with path.open() as depth_file:
            content = json.load(depth_file)
            if BIDS in content.keys() and ASKS in content.keys():
                bids = np.array(content[BIDS], dtype=np.float32)
                asks = np.array(content[ASKS], dtype=np.float32)

                return np.vstack((bids, asks))

    return None


def load_orderbook_history(pair_sym: str,
                           dates: pd.Index,
                           max_lag=timedelta(days=1)):
    """
    Load orderbook history data
    Args:
        pair_sym: trading pair
        dates: dates to load
        max_lag: maximum difference between orderbook dump(earlier) and target date(later)

    Returns: dataframe with orderbook data
    """
    base_path = ORDERBOOK_PATH / pair_sym.upper()
    if not base_path.exists():
        logging.error('No orderbook data for symbol %s', pair_sym)
        return pd.DataFrame({
            DATE: [],
            ORDERBOOK: []
        })

    timestamps = [int(path.name.split('.')[0]) for path in sorted(base_path.iterdir())]
    i = 0
    orderbook = []
    for candle_dt in tqdm(dates):
        while i + 1 < len(timestamps) and datetime.fromtimestamp(timestamps[i + 1]) <= candle_dt:
            i += 1

        if i < len(timestamps) and datetime.fromtimestamp(timestamps[i]) + max_lag > candle_dt:
            orderbook.append(_read_orderbook(base_path / f'{timestamps[i]}.json'))
            i += 1
        else:
            orderbook.append(None)

    frame = pd.DataFrame({
        DATE: dates,
        ORDERBOOK: orderbook
    }).dropna()

    frame.set_index(DATE, inplace=True)
    return frame
