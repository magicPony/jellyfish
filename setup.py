from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().split()

setup(
    version='0.1',
    name='treasure_island',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            # 'dump-binance-creds=treasure_island.creds_manager:dump_binance'
        ]
    }
)
