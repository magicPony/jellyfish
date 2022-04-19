import backtesting

from jellyfish import CACHE_PATH


class Backtest(backtesting.Backtest):
    def plot(self, filepath=None, *args, **kwargs):
        """
        Plot the progression of the last backtest run.

        Args:
            filepath: file path
            **kwargs:
        """
        if filepath is None:
            filepath = (CACHE_PATH / 'test.html').as_posix()

        super(Backtest, self).plot(filename=filepath, *args, *kwargs)