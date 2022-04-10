from datetime import datetime, timedelta
from tempfile import TemporaryDirectory
from unittest import TestCase

from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from backtesting.test import SMA

from treasure_island.candles_loader import load_candles_history
from treasure_island.indicators import heiken_ashi
from treasure_island.utils import load_binance_client


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 50
    n2 = 200

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

        self.I(heiken_ashi, self.data.df, name='Heiken Ashi')

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


class Test(TestCase):
    def test_heiken_ashi(self):
        client = load_binance_client()
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(days=365 * 2)
        pair = 'XRPUSDT'
        interval = '1d'
        frame = load_candles_history(client, pair, start_dt, end_dt, interval)

        # fucking "summer time" +-one hour causing problems with timestamps
        frame = frame.reset_index()
        frame.Date = frame.Date.dt.date
        frame.set_index('Date', inplace=True)

        bt = Backtest(frame, SmaCross, cash=10_000, commission=.002, trade_on_close=True)
        stats = bt.run()

        with TemporaryDirectory() as temp_dir:
            bt.plot(filename=f'{temp_dir}/test.html')

        assert stats['# Trades'] > 0
