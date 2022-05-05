import numpy as np
import torch
from torch.utils.data import Dataset


class IndicatorsDataset(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray, *, depth, change_thr):
        self.y = []
        self.x = []
        for i in range(depth, len(x) + 1):
            if np.abs(y[i - 1]) > change_thr:
                self.x += [x[i - depth:i].tolist()]
                self.y += [y[i - 1]]

        self.x = np.array(self.x, dtype=np.float32)
        for i in range(self.x.shape[-1]):
            tmp = self.x[:, :, i]
            self.x[:, :, i] = (tmp - tmp.mean()) / tmp.std()

        self.y = np.expand_dims(self.y, axis=-1).astype(np.float32)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return torch.FloatTensor(self.x[i]), torch.FloatTensor(self.y[i])
