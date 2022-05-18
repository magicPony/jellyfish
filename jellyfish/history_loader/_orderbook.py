import json
import logging
from typing import List
import pandas as pd
from datetime import datetime

import numpy as np
from tqdm.auto import tqdm

from jellyfish.constants import ORDERBOOK_PATH, DATE, ORDERBOOK


def load_orderbook_history(pair_sym: str,
                           dates: List[datetime] = None,
                           start_dt: datetime = None,
                           end_dt: datetime = None):
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
    print(len(timestamps))
    timestamps = timestamps
    for ts in tqdm(timestamps):
        depth = None
        depth_path = base_path / f'{ts}.json'
        if depth_path.exists():
            with depth_path.open() as depth_file:
                content = json.load(depth_file)
                bids = content['bids']
                asks = content['asks']

                depth = np.vstack((bids, asks))

        orderbook.append(depth)

    df = pd.DataFrame({
        DATE: [datetime.fromtimestamp(ts) for ts in timestamps],
        ORDERBOOK: orderbook
    })

    return df.set_index('Date')
