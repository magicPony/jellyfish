"""
Orderbook history data loading module
"""
import json
import logging
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from jellyfish.constants import ORDERBOOK_PATH, DATE, ORDERBOOK


def load_orderbook_history(pair_sym: str,
                           dates: List[datetime] = None,
                           start_dt: datetime = None,
                           end_dt: datetime = None):
    """
    Load orderbook data
    Args:
        pair_sym: trading pair
        dates: dates to load data
        start_dt: history start date
        end_dt: history last date

    Returns: dataframe with orderbook data
    """
    base_path = ORDERBOOK_PATH / pair_sym.upper()
    if not base_path.exists():
        logging.error('No orderbook data for symbol %s', pair_sym)
        return pd.DataFrame({
            DATE: [],
            ORDERBOOK: []
        })

    if dates is None:
        timestamps = [int(path.name.split('.')[0]) for path in sorted(base_path.iterdir())]
        timestamps = [ts for ts in timestamps if start_dt.timestamp() <= ts <= end_dt.timestamp()]
    else:
        timestamps = [int(dt.timestamp()) for dt in dates]

    orderbook = []
    for ts in tqdm(timestamps):
        depth = None
        depth_path = base_path / f'{ts}.json'
        if depth_path.exists():
            with depth_path.open() as depth_file:
                content = json.load(depth_file)
                bids = content['bids']
                asks = content['asks']

                depth = np.vstack((bids[::-1], asks))

        orderbook.append(depth)

    frame = pd.DataFrame({
        DATE: [datetime.fromtimestamp(ts) for ts in timestamps],
        ORDERBOOK: orderbook
    })

    frame.set_index(DATE, inplace=True)
    return frame
