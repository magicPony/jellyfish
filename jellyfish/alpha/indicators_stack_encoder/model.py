import torch


class IndicatorsEncoder(torch.nn.Module):
    def __init__(self, features_num, depth):
        super().__init__()
        self.fcn = torch.nn.Sequential(
            torch.nn.Linear(features_num, features_num // 2),
            torch.nn.ReLU(),
            torch.nn.Linear(features_num // 2, features_num // 4),
            torch.nn.ReLU(),
            torch.nn.Linear(features_num // 4, features_num // 8),
            torch.nn.ReLU(),
            torch.nn.Linear(features_num // 8, features_num // 16),
            torch.nn.ReLU(),
            torch.nn.Linear(features_num // 16, 3),
            torch.nn.ReLU(),
        )
        self.conv = torch.nn.Conv2d(depth, 1, 1)

    def forward(self, x: torch.Tensor):
        x = self.fcn(x).unsqueeze(-1)
        x = self.conv(x)
        x = torch.softmax(x, dim=-1)
        return x.squeeze(axis=-1).squeeze(axis=-1)
