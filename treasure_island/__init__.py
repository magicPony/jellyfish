"""
Application for trading backtesting
"""
from pathlib import Path

BASE_PATH = Path(__file__).parent

PRIVATE_DATA_PATH = BASE_PATH / 'private_data'
CACHE_PATH = BASE_PATH / '.cache'
CANDLES_HISTORY_PATH = CACHE_PATH / 'candles_history'
