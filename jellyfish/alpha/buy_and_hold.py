"""
Simple buy&hold strategy
"""
from jellyfish.core import Strategy


class BuyAndHold(Strategy):
    """
    Simple buy&hold strategy
    """
    def next(self):
        if len(self.trades) == 0:
            self.buy()
