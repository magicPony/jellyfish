from datetime import datetime, timedelta
from unittest import TestCase

from jellyfish import indicator
from jellyfish.candles_loader import load_candles_history
from jellyfish.core import Backtest, Strategy, Client


class DummyStrategyWithIndicators(Strategy):
    def init(self):
        self.I(indicator.dumb_sr_lines, self.data.High, self.data.Low, name='S/R line',
               overlay=True)
        self.I(indicator.wad, self.data.High, self.data.Low, self.data.Close,
               name='Williams Accumulation/Distribution')
        self.I(indicator.will_r, self.data.High, self.data.Low, self.data.Close,
               name='Williams %R')
        self.I(indicator.wilders, self.data.Close, 5, name='Wilders Smoothing [fast]',
               overlay=True)
        self.I(indicator.wilders, self.data.Close, 20, name='Wilders Smoothing [slow]',
               overlay=True)
        self.I(indicator.wilders, self.data.Close, 40, name='Wilders Smoothing [very slow]',
               overlay=True)
        self.I(indicator.stoch_rsi, self.data.Close, name='Stochastic RSI')
        self.I(indicator.stoch, self.data.High, self.data.Low, self.data.Close,
               name='Stochastic Oscillator')
        self.I(indicator.aroon, self.data.High, self.data.Low)
        self.I(indicator.aroon_oscillator, self.data.High, self.data.Low, name='Aroon Oscillator')
        self.I(indicator.fisher, self.data.High, self.data.Low, name='Fished')
        self.I(indicator.cmo, self.data.Close, name='Chande Momentum Oscillator')
        self.I(indicator.bop, self.data.Open, self.data.High, self.data.Low,
               self.data.Close, name='Balance of Power')
        self.I(indicator.dpo, self.data.Close, name='Detrended Price Oscillator')
        self.I(indicator.kvo, self.data.High, self.data.Low, self.data.Close, self.data.Volume,
               15, 25, name='Klinger Volume Oscillator')
        self.I(indicator.lag, self.data.Close, name='Lag', overlay=True)
        self.I(indicator.mass, self.data.High, self.data.Low, name='Mass')
        self.I(indicator.rsi, self.data.Close, 20)
        self.I(indicator.bollinger_bands, self.data.df, 10, 1.5, name='Bollinger bands')
        self.I(indicator.ema, self.data.Close, 20, 1.5, name='EMA')
        self.I(indicator.sma, self.data.Close, 20, name='SMA', overlay=True)
        self.I(indicator.macd, self.data.Close, 12, 26, 9)
        self.I(indicator.awesome, self.data.High, self.data.Low, name='Awesome')

        Strategy.init(self)


class Test(TestCase):
    def test_indicators(self):
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(days=30 * 4)
        frame = load_candles_history(Client(), 'BTCUSDT', start_dt, end_dt, '4h')

        frame['i_zigzag'] = indicator.zigzag(frame.Close.to_numpy(), 2e-2)
        frame['i_hurst_random_walk'] = indicator.hurst(frame.Close.to_numpy())
        frame['i_hurst_change'] = indicator.hurst(frame.Close.to_numpy(), 100, 'change')
        frame['i_hurst_price'] = indicator.hurst(frame.Close.to_numpy(), 200, 'price')

        backtest = Backtest(frame.reset_index(), DummyStrategyWithIndicators)
        backtest.run()
        backtest.plot()
