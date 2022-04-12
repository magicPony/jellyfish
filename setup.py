from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().split()

setup(
    version='0.1',
    name='marlin',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'rm-candles=marlin.cli:clean_candles_cache',
            'load-candles=marlin.cli:download_candles'
        ]
    }
)
