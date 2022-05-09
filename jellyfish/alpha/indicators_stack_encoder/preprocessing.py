import pandas as pd
from jellyfish import indicator


def add_indicators(df: pd.DataFrame, open_col, high_col, low_col, close_col):
    df['Return'] = df[close_col] / df[open_col] - 1

    df['i_wad'] = indicator.wad(df[high_col], df[low_col], df[close_col])
    for period in [2, 3, 5, 8, 15, 25, 35]:
        df[f'i_will_r_{period}'] = indicator.will_r(df[high_col], df[low_col],
                                                    df[close_col], period)
        df[f'i_wilders_{period}'] = indicator.wilders(df[close_col], period)
        df[f'i_stoch_rsi_{period}'] = indicator.stoch_rsi(df[close_col], period)

        fisher = indicator.fisher(df[high_col], df[low_col], period)
        df[f'i_fisher1_{period}'] = fisher[0]
        df[f'i_fisher2_{period}'] = fisher[1]

        df[f'i_cmo_{period}'] = indicator.cmo(df[close_col], period)
        df[f'i_bop_{period}'] = indicator.bop(df[open_col], df[high_col],
                                              df[low_col], df[close_col])
        df[f'i_dpo_{period}'] = indicator.dpo(df[close_col], period)
        df[f'i_mass_{period}'] = indicator.mass(df[high_col], df[low_col], period)

        aroon = indicator.aroon(df[high_col], df[low_col], period)
        df[f'i_aroon_low_{period}'] = aroon[0]
        df[f'i_aroon_high_{period}'] = aroon[1]

        sr = indicator.dumb_sr_lines(df[high_col], df[low_col], period)
        df[f'i_support_{period}'] = sr[0]
        df[f'i_resistance_{period}'] = sr[1]

        df[f'i_aroon_osc_{period}'] = indicator.aroon_oscillator(df[high_col],
                                                                 df[low_col], period)
        df[f'i_rsi_{period}'] = indicator.rsi(df[close_col], period)

    # period must be greater than 100
    df[f'i_hurst_random_{period}'] = indicator.hurst(df[close_col],
                                                     kind=indicator.HURST_RANDOM_WALK)
    df[f'i_hurst_price_{period}'] = indicator.hurst(df[close_col], kind=indicator.HURST_PRICE)
    df[f'i_hurst_change_{period}'] = indicator.hurst(df[close_col], kind=indicator.HURST_CHANGE)

    df.dropna(inplace=True)

    return df
