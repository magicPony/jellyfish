"""
Public constants
"""
from pathlib import Path

BASE_PATH = Path(__file__).parent

# Path constants
RESOURCES_PATH = BASE_PATH / 'resources'
CACHE_PATH = RESOURCES_PATH / '.cache'
ORDERBOOK_PATH = RESOURCES_PATH / 'orderbook'
CANDLES_DB_PATH = CACHE_PATH / 'candles.db'
DOTENV_PATH = RESOURCES_PATH / '.env'

# Frame column names
DATE = 'Date'
OPEN = 'Open'
HIGH = 'High'
LOW = 'Low'
CLOSE = 'Close'
VOLUME = 'Volume'
NUM_OF_TRADES = 'NumOfTrades'
QUOTE_ASSET_VOLUME = 'QuoteAssetVolume'
TAKER_BUY_ASSET_VOLUME = 'TakerBuyAssetVolume'
TAKER_SELL_ASSET_VOLUME = 'TakerSellAssetVolume'
ORDERBOOK = 'Orderbook'


def create_directories():
    for dir_path in (RESOURCES_PATH, CACHE_PATH, ORDERBOOK_PATH):
        dir_path.mkdir(exist_ok=True, parents=True)


create_directories()
