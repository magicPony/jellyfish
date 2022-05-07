from torch import Tensor
from torch.nn import Module, Linear, ReLU, Softmax, Sequential, Conv2d


class IndicatorsEncoder(Module):
    def __init__(self, depth, features_num):
        super().__init__()
        self.fcn = Sequential(
            Linear(features_num, features_num // 2),
            ReLU(),
            Linear(features_num // 2, features_num // 4),
            ReLU(),
            Linear(features_num // 4, features_num // 8),
            ReLU(),
            Linear(features_num // 8, features_num // 16),
            ReLU(),
            Linear(features_num // 16, 3),
            ReLU(),
        )
        self.softmax = Softmax(dim=2)
        self.conv = Conv2d(depth, 1, 1)

    def forward(self, x: Tensor):
        x = self.fcn(x).unsqueeze(-1)
        x = self.conv(x)
        x = self.softmax(x)
        return x.squeeze()
