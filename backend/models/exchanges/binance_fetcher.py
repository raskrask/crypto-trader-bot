import ccxt
import pandas as pd
import boto3
from io import BytesIO
from datetime import datetime, timedelta, timezone
from config.settings import settings

class BinanceFetcher:

    def __init__(self):
        self.binance = ccxt.binance()


    def fetch_ohlcv(self, symbol, interval, days, limit):
        # `days` 日前の00:00を起点にデータを取得
        since = self.binance.parse8601((datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%dT00:00:00Z'))        
        candles = self.binance.fetch_ohlcv(symbol, timeframe=interval, since=since, limit=limit)

        # DataFrame に変換
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        return df

    def fetch_daily_ohlcv(self, symbol, interval_min, days):
        """
        ccxt を使って Binance から VITE/USDT の過去データを取得
        """
        # `days` 日前の00:00を起点にデータを取得
        since = self.binance.parse8601((datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%dT00:00:00Z'))        
        limit = int(24*60 / interval_min) # 24時間分
        timeframe = f"{interval_min}m"
        if interval_min >= 60 * 24:
            timeframe = f"{interval_min//60//24}d"
        elif interval_min >= 60:
            timeframe = f"{interval_min//60}h"
        candles = self.binance.fetch_ohlcv(symbol, timeframe=f"{timeframe}", since=since, limit=limit)

        # DataFrame に変換
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        return df

