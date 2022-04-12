from datetime import datetime, timedelta
from unittest import TestCase

from backtesting import Backtest

from jellyfish.candles_loader import load_candles_history
from jellyfish.indicator import heiken_ashi
from jellyfish.stretegy import SmaCross
from jellyfish.utils import load_binance_client, plot_ohlc


class SmaCrossWithHaIndicator(SmaCross):
    def init(self):
        self.I(heiken_ashi, self.data.df, name='Heiken Ashi')
        super(SmaCrossWithHaIndicator, self).init()


class Test(TestCase):
    def test_heiken_ashi_strategy(self):
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

        bt = Backtest(frame, SmaCrossWithHaIndicator, cash=10_000, commission=.002, trade_on_close=True)
        stats = bt.run()
        plot_ohlc(bt, open_browser=False)

        assert stats['# Trades'] > 0
