import numpy as np
import torch
from torch.nn.functional import one_hot
from torch.utils.data import Dataset


class IndicatorsDataset(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray, means=None, stds=None, *, depth):
        self.x = []
        for i in range(depth, len(x) + 1):
            self.x += [x[i - depth:i].tolist()]

        self.x = np.array(self.x, dtype=np.float32)
        self.y = y.astype(np.float32) + 1

        if means is None:
            means = [self.x[:, :, i].mean() for i in range(self.x.shape[-1])]

        if stds is None:
            stds = [self.x[:, :, i].std() for i in range(self.x.shape[-1])]

        for i in range(self.x.shape[-1]):
            self.x[:, :, i] = (self.x[:, :, i] - means[i]) / stds[i]

        self.means = means
        self.stds = stds
        self.y = np.expand_dims(self.y, axis=-1)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        x = torch.FloatTensor(self.x[i])
        y = torch.LongTensor(self.y[i])
        y = one_hot(y, 3).float()
        return x, y.squeeze()
