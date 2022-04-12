"""
Application for trading backtesting
"""
from pathlib import Path

BASE_PATH = Path(__file__).parent

RESOURCES_PATH = BASE_PATH / 'resources'

PRIVATE_DATA_PATH = RESOURCES_PATH / 'private_data'
CACHE_PATH = RESOURCES_PATH / '.cache'
CANDLES_HISTORY_PATH = CACHE_PATH / 'candles_history'
