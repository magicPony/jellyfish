from jellyfish.core import Strategy


class BuyAndHold(Strategy):
    def next(self):
        if len(self.trades) == 0:
            self.buy()