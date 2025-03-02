import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models.crypto_training_dataset import CryptoTrainingDataset
from models.exchanges.binance_fetcher import BinanceFetcher
from models.exchanges.coingecko_api import CoinGeckoAPI
from config.config_manager import get_config_manager

class EdaService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()

    def explore(self):
        self.crypto_data = CryptoTrainingDataset()
        self.fetcher = BinanceFetcher()
        self.coin_gecko = CoinGeckoAPI()

        result = {}

        # BTC ドミナンス
        result["market"] =  {
            "btc_dominance": self.coin_gecko.get_btc_dominance(),
            "btc_market_cap": self.coin_gecko.get_market_cap()
        }

        # ohlcv chart
        for symbol in ['VITE/USDT', 'BTC/USDT']:
            data = self.fetcher.fetch_ohlcv(symbol, "1d", 60, 30)
            result[symbol] = data

        return result
