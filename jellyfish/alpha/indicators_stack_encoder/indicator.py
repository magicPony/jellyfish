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
    FEATURES_NUM = 79

    def __init__(self, open_col=OPEN, high_col=HIGH, low_col=LOW,
                 close_col=CLOSE, change_thr=0.01, depth=3):
        self.open_col = open_col
        self.high_col = high_col
        self.low_col = low_col
        self.close_col = close_col
        self.change_thr = change_thr
        self.depth = depth

        self._means = None
        self._stds = None

        self.model = None

    def _pick_threshold(self, loader: DataLoader):
        predictions = []
        targets = []
        for x, y in loader:
            y_pred = self.model(x)
            predictions.append(y_pred.detach().numpy())
            targets.append(y.numpy())

        predictions = np.concatenate(predictions)
        targets = np.concatenate(targets)
        return np.mean(targets)

    def fit(self, df: pd.DataFrame):
        df = add_indicators(df.copy(), self.open_col, self.high_col, self.low_col, self.close_col)
        indicator_cols = [c for c in df.columns if c.startswith('i_')]
        dataset = IndicatorsDataset(df[indicator_cols].to_numpy(),
                                    (df.Return.rolling(3).sum() // self.change_thr).fillna(0),
                                    depth=self.depth)
        self._means = dataset.means
        self._stds = dataset.stds

        loader = DataLoader(dataset=dataset, batch_size=100, shuffle=True)
        criterion = torch.nn.CrossEntropyLoss(reduction='mean')
        self.model = IndicatorsEncoder(dataset[0][0].shape[0], dataset[0][0].shape[1])
        optimizer = torch.optim.Adam(self.model.parameters(), lr=2e-3)

        train_history, _ = train_loop(self.model, loader, criterion, optimizer, epochs_num=110)

        self.threshold = self._pick_threshold(loader)

        plt.title('Train loss history')
        plt.plot(train_history)
        plt.show()

    def transform(self, df: pd.DataFrame, date_col=DATE):
        dates = df[date_col].tolist()
        print('Input len:', len(df))
        df = add_indicators(df.copy(), self.open_col, self.high_col,
                            self.low_col, self.close_col)
        print('Preprocessing len:', len(df))
        indicator_cols = [c for c in df.columns if c.startswith('i_')]
        dataset = IndicatorsDataset(df[indicator_cols].to_numpy(), df.target,
                                    depth=self.depth, means=self._means, stds=self._stds)
        loader = DataLoader(dataset=dataset, batch_size=300, shuffle=True)
        prediction = []
        for x, _ in loader:
            y_pred = self.model(x)
            prediction.append(y_pred.detach().numpy().flatten())

        prediction = np.concatenate(prediction)
        ret = np.zeros((len(dates))) * np.nan
        index = 0
        for date, signal in zip(df[date_col].tolist(), prediction):
            while dates[index] < date:
                index += 1

            ret[index] = 1 if signal > self.threshold else -1

        return ret
