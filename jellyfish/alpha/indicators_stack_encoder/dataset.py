import numpy as np
import torch
from torch.utils.data import Dataset


class IndicatorsDataset(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray, means=None, stds=None, *, depth):
        self.x = []
        for i in range(depth, len(x) + 1):
            self.x += [x[i - depth:i].tolist()]

        self.x = np.array(self.x, dtype=np.float32)
        self.y = np.expand_dims(y[depth - 1:], axis=-1).astype(np.float32)

        if means is None:
            means = [self.x[:, :, i].mean() for i in range(self.x.shape[-1])]

        if stds is None:
            stds = [self.x[:, :, i].std() for i in range(self.x.shape[-1])]

        for i in range(self.x.shape[-1]):
            self.x[:, :, i] = (self.x[:, :, i] - means[i]) / stds[i]

        self.means = means
        self.stds = stds

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return torch.FloatTensor(self.x[i]), torch.FloatTensor(self.y[i])
