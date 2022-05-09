from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from jellyfish.alpha.indicators_stack_encoder.dataset import IndicatorsDataset
from jellyfish.alpha.indicators_stack_encoder.model import IndicatorsEncoder
from jellyfish.alpha.indicators_stack_encoder.preprocessing import add_indicators
from jellyfish.constants import (OPEN, HIGH, LOW, CLOSE, DATE)
from jellyfish.train import train_loop


class Indicator:
    def __init__(self, open_col=OPEN, high_col=HIGH, low_col=LOW,
                 close_col=CLOSE, date_col=DATE, change_thr=0.01, depth=3):
        self.open_col = open_col
        self.high_col = high_col
        self.low_col = low_col
        self.close_col = close_col
        self.date_col = date_col
        self.change_thr = change_thr
        self.depth = depth

        self._means = None
        self._stds = None

        self.model = None

    @staticmethod
    def _pick_threshold(loader: DataLoader):
        targets = [y.numpy() for _, y in loader]
        return np.concatenate(targets).mean()

    def fit_transform(self, df: pd.DataFrame, train_size: Union[float, int] = 0.8):
        if isinstance(train_size, float):
            train_size = int(len(df) * train_size)

        self.fit(df.iloc[:train_size])
        result = self.transform(df.iloc[train_size:])
        prefix = np.zeros((len(df) - len(result))) * np.nan
        return np.concatenate([prefix, result])

    def fit(self, df: pd.DataFrame):
        df = add_indicators(df.copy(), self.open_col, self.high_col, self.low_col, self.close_col)
        indicator_cols = [c for c in df.columns if c.startswith('i_')]

        features = df[indicator_cols].to_numpy()
        target = np.clip((df.Return.rolling(2).sum() // self.change_thr).fillna(0),
                         -1, 1)[self.depth - 1:]

        dataset = IndicatorsDataset(features, target, depth=self.depth)
        self._means = dataset.means
        self._stds = dataset.stds

        loader = DataLoader(dataset=dataset, batch_size=100, shuffle=True)
        criterion = torch.nn.CrossEntropyLoss(reduction='mean')
        self.model = IndicatorsEncoder(dataset[:1][0].shape[-2], dataset[:1][0].shape[-1])
        optimizer = torch.optim.Adam(self.model.parameters(), lr=2e-3)

        train_history, _ = train_loop(self.model, loader, criterion, optimizer, epochs_num=150)

        self.threshold = self._pick_threshold(loader)

        plt.title('Train loss history')
        plt.plot(train_history)
        plt.show()

    def transform(self, df: pd.DataFrame, suppress_neutrals=True):
        dates = df[self.date_col].tolist()
        df = add_indicators(df.copy(), self.open_col, self.high_col, self.low_col, self.close_col)
        indicator_cols = [c for c in df.columns if c.startswith('i_')]

        features = df[indicator_cols].to_numpy()
        target = np.zeros_like(df.Return.to_numpy())[self.depth - 1:]

        dataset = IndicatorsDataset(features, target, depth=self.depth,
                                    means=self._means, stds=self._stds)

        loader = DataLoader(dataset=dataset, batch_size=300)
        prediction = []
        for x, _ in loader:
            y_pred = self.model(x)
            prediction.append(y_pred.detach().numpy().argmax(axis=-1).tolist())

        prediction = np.concatenate(prediction)
        if suppress_neutrals:
            prediction = [-1 if p < self.threshold else 1 for p in prediction]

        plt.plot(prediction)
        plt.title('Predictions')
        plt.show()

        ret = np.zeros((len(dates))) * np.nan
        index = 0
        for date, signal in zip(df[self.date_col].tolist(), prediction):
            while dates[index] < date:
                index += 1

            ret[index] = signal

        return ret
