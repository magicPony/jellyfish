"""
Machine learning tools
"""
import torch
from torch.utils.data import DataLoader

from tqdm.auto import trange


def feed_forward(model: torch.nn.Module,
                 loader: DataLoader,
                 criterion):
    """
    Emulate forward epoch
    Args:
        model: pytorch model
        loader: data loader
        criterion: loss/accuracy callable

    Returns: loss tensor
    """
    loss = 0
    for X, y in loader:
        y_pred = model(X)
        loss += criterion(y, y_pred)

    return loss / len(loader)


def train_loop(model: torch.nn.Module,
               loader: DataLoader,
               criterion,
               optimizer,
               epochs_num: int = 10,
               val_loader: DataLoader = None,
               val_criterion=None):
    """
    Train loop
    Args:
        model: pytorch model
        loader: data loader
        criterion: learning criterion
        optimizer: optimizer
        epochs_num: epochs number
        val_loader: validation loader
        val_criterion: validation criterion/accuracy

    Returns: train/val history
    """
    train_history = []
    val_history = []
    for _ in trange(epochs_num):
        if val_loader is not None:
            with torch.no_grad():
                loss = feed_forward(model, val_loader, val_criterion or criterion).item()
                val_history.append(loss)

        loss = feed_forward(model, loader, criterion)
        train_history.append(loss.item() / len(loader))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return train_history, val_history
