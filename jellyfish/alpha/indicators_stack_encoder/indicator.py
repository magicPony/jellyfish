import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from jellyfish import indicator
from jellyfish.alpha.indicators_stack_encoder.dataset import IndicatorsDataset
from jellyfish.alpha.indicators_stack_encoder.model import IndicatorsEncoder
from jellyfish.constants import (OPEN, HIGH, LOW, CLOSE)
from jellyfish.train import train_loop


def preprocess_data(df: pd.DataFrame, open_col, high_col, low_col, close_col):
    df['i_wad'] = indicator.wad(df[high_col], df[low_col], df[close_col])
    for period in [3, 5, 8, 15, 25]:
        df[f'i_will_r_{period}'] = indicator.will_r(df[high_col], df[low_col],
                                                    df[close_col], period)
        df[f'i_wilders_{period}'] = indicator.wilders(df[close_col], period)
        df[f'i_stoch_rsi_{period}'] = indicator.stoch_rsi(df[close_col], period)

        fisher = indicator.fisher(df[high_col], df[low_col], period)
        df[f'i_fisher1_{period}'] = fisher[0]
        df[f'i_fisher2_{period}'] = fisher[1]

        df[f'i_cmo_{period}'] = indicator.cmo(df[close_col], period)
        df[f'i_bop_{period}'] = indicator.bop(df[open_col], df[high_col],
                                              df[low_col], df[close_col])
        df[f'i_dpo_{period}'] = indicator.dpo(df[close_col], period)
        df[f'i_mass_{period}'] = indicator.mass(df[high_col], df[low_col], period)

        aroon = indicator.aroon(df[high_col], df[low_col], period)
        df[f'i_aroon_low_{period}'] = aroon[0]
        df[f'i_aroon_high_{period}'] = aroon[1]

        sr = indicator.dumb_sr_lines(df[high_col], df[low_col], period)
        df[f'i_support_{period}'] = sr[0]
        df[f'i_resistance_{period}'] = sr[1]

        df[f'i_aroon_osc_{period}'] = indicator.aroon_oscillator(df[high_col],
                                                                 df[low_col], period)
        df[f'i_rsi_{period}'] = indicator.rsi(df[close_col], period)

    # period must be greater than 100
    df[f'i_hurst_random_{period}'] = indicator.hurst(df[close_col],
                                                     kind=indicator.HURST_RANDOM_WALK)
    df[f'i_hurst_price_{period}'] = indicator.hurst(df[close_col], kind=indicator.HURST_PRICE)
    df[f'i_hurst_change_{period}'] = indicator.hurst(df[close_col], kind=indicator.HURST_CHANGE)
    df['Return'] = df[close_col] / df[open_col] - 1

    df['target'] = df['Return'].rolling(3).sum().to_numpy().astype(np.float32)
    df.dropna(inplace=True)

    return df


class Indicator:
    FEATURES_NUM = 79

    def __init__(self, open_col=OPEN, high_col=HIGH, low_col=LOW,
                 close_col=CLOSE, change_thr=0.01, depth=3):
        self.open_col = open_col
        self.high_col = high_col
        self.low_col = low_col
        self.close_col = close_col
        self.change_thr = change_thr
        self.depth = depth
        self.model = IndicatorsEncoder(Indicator.FEATURES_NUM, depth)

    def fit(self, df: pd.DataFrame):
        df = preprocess_data(df.copy(), self.open_col, self.high_col, self.low_col, self.close_col)
        df.dropna(inplace=True)

        indicator_cols = [c for c in df.columns if c.startswith('i_')]
        dataset = IndicatorsDataset(df[indicator_cols].to_numpy(), df['target'], depth=self.depth,
                                    change_thr=self.change_thr)
        loader = DataLoader(dataset=dataset, batch_size=300, shuffle=True)

        self.model = IndicatorsEncoder(len(indicator_cols), self.depth)
        criterion = torch.nn.HuberLoss(reduction='mean')
        optimizer = torch.optim.Adam(self.model.parameters(), lr=2e-3)

        train_history, _ = train_loop(self.model, loader, criterion, optimizer, epochs_num=110)

        plt.plot(train_history)
        plt.show()
