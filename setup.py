from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().split()

setup(
    version='0.1',
    name='jellyfish',
    packages=['jellyfish'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            # candlestick data loading
            'rm-candles=jellyfish.cli:clean_candles_cache',
            'load-candles=jellyfish.cli:download_candles',

            # orderbook crawler
            'crawler=jellyfish.cli:crawler_cli'
        ]
    }
)
