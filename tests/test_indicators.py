from datetime import datetime, timedelta
from unittest import TestCase

import numpy as np
import plotly.express as px

from jellyfish import indicator
from jellyfish.core import Strategy, Backtest
from jellyfish.history_loader import load_candles_history


class DummyWithIndicators(Strategy):
    def init(self):
        super(DummyWithIndicators, self).init()
        self.I(indicator.dumb_sr_lines, self.data.High, self.data.Low)
        self.I(indicator.stoch, self.data.High, self.data.Low, self.data.Close)
        self.I(indicator.aroon, self.data.High, self.data.Low)
        self.I(indicator.fisher, self.data.High, self.data.Low)
        self.I(indicator.bollinger_bands, self.data.df, 10, 1.5)
        self.I(indicator.macd, self.data.Close, 12, 26, 9)

        for lvl in indicator.volume_profile_valleys(self.data.Close, self.data.Volume, 50):
            self.plot_hline(lvl, name='Volume Profile', color='blue')

        for lvl in indicator.fib_retracement(self.data.High, self.data.Low):
            self.plot_hline(lvl, name='Fib', color='orange')


class Test(TestCase):
    def test_volume_profile(self):
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(days=30 * 4)
        frame = load_candles_history('BTCUSDT', start_dt, end_dt, '4h')

        prices = frame.Close.to_numpy()
        volumes = frame.Volume.to_numpy()

        bins_num = 150
        price_range = prices.min(), prices.max()
        bin_size = (price_range[1] - price_range[0]) / bins_num
        bins = np.arange(price_range[1], price_range[0], -bin_size)[::-1]

        profile = indicator.volume_profile(prices, volumes, bins=bins)
        fig = px.bar(x=profile, y=bins, orientation='h')
        fig.show()

    def test_indicators(self):
        end_dt = datetime(year=2022, month=2, day=3)
        start_dt = end_dt - timedelta(days=30 * 4)
        frame = load_candles_history('BTCUSDT', start_dt, end_dt, '4h')

        frame['i_hurst_random_walk'] = indicator.hurst(frame.Close)
        frame['i_hurst_change'] = indicator.hurst(frame.Close, 100, indicator.HURST_CHANGE)
        frame['i_hurst_price'] = indicator.hurst(frame.Close, 200, indicator.HURST_PRICE)
        frame['i_wad'] = indicator.wad(frame.High, frame.Low, frame.Close)
        frame['i_will_r'] = indicator.will_r(frame.High, frame.Low, frame.Close)
        frame['i_wilders_fast'] = indicator.wilders(frame.Close, 5)
        frame['i_wilders_slow'] = indicator.wilders(frame.Close, 20)
        frame['i_wilders_very_slow'] = indicator.wilders(frame. Close, 40)
        frame['i_stoch_rsi'] = indicator.stoch_rsi(frame.Close)
        frame['i_aroon_osc'] = indicator.aroon_oscillator(frame.High, frame.Low)
        frame['i_cmo'] = indicator.cmo(frame.Close)
        frame['i_bop'] = indicator.bop(frame.Open, frame.High, frame.Low, frame.Close)
        frame['i_dpo'] = indicator.dpo(frame.Close)
        frame['i_kvo'] = indicator.kvo(frame.High, frame.Low, frame.Close, frame.Volume, 15, 25)
        frame['i_mass'] = indicator.mass(frame.High, frame.Low)
        frame['i_rsi'] = indicator.rsi(frame.Close, 20)
        frame['i_ema'] = indicator.ema(frame.Close, 20, 1.5)
        frame['i_sma'] = indicator.sma(frame.Close, 20)
        frame['i_awesome'] = indicator.awesome(frame.High, frame.Low)
        frame['i_price_lag'] = indicator.lag(frame.Close, 1)
        frame['i_mfi'] = indicator.mfi(frame.High, frame.Low, frame.Close, frame.Volume, 25)
        frame['i_marketfi'] = indicator.marketfi(frame.High, frame.Low, frame.Volume)

        backtest = Backtest(frame, DummyWithIndicators)
        backtest.run()
        backtest.plot()
