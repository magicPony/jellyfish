"""
Public constants
"""
from pathlib import Path

BASE_PATH = Path(__file__).parent

RESOURCES_PATH = BASE_PATH / 'resources'

PRIVATE_DATA_PATH = RESOURCES_PATH / 'private_data'
CACHE_PATH = RESOURCES_PATH / '.cache'
CANDLES_HISTORY_PATH = CACHE_PATH / 'candles_history'


DATE = 'Date'
OPEN = 'Open'
HIGH = 'High'
LOW = 'Low'
CLOSE = 'Close'
VOLUME = 'Volume'
NUM_OF_TRADES = 'NumOfTrades'
QUOTE_ASSET_VOLUME = 'QuoteAssetVolume'
