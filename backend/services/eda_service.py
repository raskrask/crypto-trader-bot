import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder
from scipy.signal import find_peaks
from datetime import datetime, timedelta
from models.crypto_training_dataset import CryptoTrainingDataset
from models.exchanges.binance_fetcher import BinanceFetcher
from models.exchanges.yfinance_fetcher import YFinanceFetcher
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

    # ボックス相場の検出
    # 
    def box_market_price (self):
        #self.fetcher = BinanceFetcher()
        #symbol = 'BTC/USDT'
        #data = self.fetcher.fetch_ohlcv(symbol, "1d", 360, 360)
        #df = pd.DataFrame(data)

        fetcher = YFinanceFetcher()
        symbol = '6758.T'
        df = fetcher.fetch_last_n_months(symbol, n=12)
        print(df.head())


        window_size = 20
        df['rolling_max'] = df['high'].rolling(window=window_size).max()
        df['rolling_min'] = df['low'].rolling(window=window_size).min()
        df['sma'] = df['close'].rolling(window=window_size).mean()
        df['std'] = df['close'].rolling(window=window_size).std()
        df['bb_width'] = 2 * df['std'] / df['sma']






        df['sma'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['bb_width'] = 2 * df['std'] / df['sma']

        df['in_box'] = df['bb_width'] >= 0.1  # 例: 10%以上

        self._detect_high_volume_days(df)
        self._detect_peak_points(df)
        #self._find_box_market_periods(df)



        import ta  # ADX などを使う
        try:
            adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()
        except ValueError:
            adx = None
        df['adx'] = adx
        df['in_box'] = (df['adx'] < 25)

        # ボックス相場の検出（移動平均の水平度 + ボラティリティの低さ）
        flat_threshold = 0.01   
        volatility_threshold = 0.03
#        df["sma20"] = df["close"].rolling(window=20).mean()
#        df["sma20_diff"] = df["sma20"].diff() / df["close"]
        df["sma10_max"] = df["rolling_max"].rolling(window=10).mean()
        df["sma10_max_diff"] = df["sma10_max"].diff() / df["rolling_max"]
        df["sma10_min"] = df["rolling_min"].rolling(window=10).mean()
        df["sma10_min_diff"] = df["sma10_min"].diff() / df["rolling_min"]

        df["volatility"] = df["close"].rolling(window=5).std() / df["close"]

        df["is_box"] = (df["sma10_max_diff"].abs() < flat_threshold) & (df["sma10_min_diff"].abs() < flat_threshold) & (df["volatility"] < volatility_threshold)

        df = df.dropna(subset=['rolling_max', 'rolling_min'])
        df = df.dropna(subset=['sma10_max_diff', 'sma10_max', 'sma10_min_diff', 'sma10_min', 'volatility'])
        df = df.dropna(subset=['low_points', 'high_points'])

        #self._search_box_market_periods2(df, high_points, low_points)

        data = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 
               'rolling_max', 'rolling_min', 'sma', 'high_points', 'low_points', 'is_high_volume',
               'in_box','volatility','bb_width','std']].to_dict(orient='records')

        return jsonable_encoder(data)

    # 出来高の多い日を検出（３ヶ月間で集計）
    def _detect_high_volume_days(self, df, window_size=90, volume_ratio=1.5, cv_threshold=0.3):

        # 2か月間の平均と標準偏差
        vol_mean = df['volume'].rolling(window=window_size).mean()
        vol_std = df['volume'].rolling(window=window_size).std()
        cv = vol_std / vol_mean

        # 平均 + 標準偏差1.5倍以上を急増と判定
        threshold = vol_mean + volume_ratio * vol_std
        df['is_high_volume'] = (df['volume'] > threshold) & (cv > cv_threshold)

    def _detect_peak_points(self, df):
        # 高値（ピーク）と安値（トラフ）の検出
        tolerance = 0.01 # 2%の許容範囲 

        peaks, _ = find_peaks(df["high"], distance=5)
        high_points = df.iloc[peaks][["timestamp", "high", "rolling_max"]].copy()
        high_points = high_points[
            (abs(high_points["high"] - high_points["rolling_max"]) 
            <= tolerance * high_points["rolling_max"])
        ]
        df['high_points'] = df["timestamp"].isin(high_points["timestamp"])

        troughs, _ = find_peaks(-df["low"], distance=5)
        low_points = df.iloc[troughs][["timestamp", "low", "rolling_min"]].copy()
        low_points = low_points[
            (abs(low_points["low"] - low_points["rolling_min"]) 
            <= tolerance * abs(low_points["rolling_min"]))
        ]
        df['low_points'] = df["timestamp"].isin(low_points["timestamp"])

    def _find_box_market_periods(self, df):
        i = len(df) - 1
        begin_box_idx = -1


    def _find_box_market_periods3(self, df):
        tolerance = 0.001
        box_width = 20

        df['in_box'] = False

        range_max = df.loc[df['high_points'], 'rolling_max'].iloc[-1]
        range_min= df.loc[df['low_points'], 'rolling_min'].iloc[-1]

        i = len(df) - 1
        begin_box_idx = -1
        while i >= 0:
            subset = df.iloc[:i+1]
            if subset['high_points'].any():
                tmp_range_max = subset.loc[subset['high_points'], 'rolling_max'].iloc[-1]
            if subset['low_points'].any():
                tmp_range_min = subset.loc[subset['low_points'], 'rolling_min'].iloc[-1]

            close = df['close'].iloc[i]

            rolling_min_max = df.loc[i-1:begin_box_idx, 'rolling_min'].max()
            rolling_max_min = df.loc[i-1:begin_box_idx, 'rolling_max'].min()
            if rolling_min_max > close or rolling_max_min < close:
                begin_box_idx = -1

            if begin_box_idx > 0:
                if not (range_min <= close <= range_max):
                    if (begin_box_idx - i) >= box_width:
                        df.loc[i+1:begin_box_idx, 'in_box'] = True
                    begin_box_idx = -1
                    range_max = min(tmp_range_max, df['rolling_max'].iloc[i])
                    range_min = min(tmp_range_min, df['rolling_min'].iloc[i])
                else:
                    if range_max < tmp_range_max < range_max * (1 + tolerance):
                        range_max = tmp_range_max
                    if range_min * (1 - tolerance) < tmp_range_min < range_min:
                        range_min = tmp_range_min

            else: # not in_box_flag
                if (range_min <= df['close'].iloc[i] <= range_max):
                    begin_box_idx = i
                else:
                    range_max = tmp_range_max
                    range_min = tmp_range_min

            i -= 1


    def _search_box_market_periods2(self, df, high_points, low_points):
        window = 20
        df['in_box'] = False

        tolerance = 0.001
        min_length = 10
        high_idx = high_points.index[-1]
        low_idx = low_points.index[-1]

        i = len(df) - 1
        while i >= 0:
            range_max = df['rolling_max'].iloc[i]
            range_min = df['rolling_min'].iloc[i]
            in_box_flag = False
            j = i

            while j >= 0:
                high_j = df['high'].iloc[j]
                low_j = df['low'].iloc[j]
                close_j = df['close'].iloc[j]

                if high_j > range_max * (1 + tolerance):
                    range_max = max(range_max, high_j)
                if low_j < range_min * (1 - tolerance):
                    range_min = min(range_min, low_j)

                if not (range_min <= close_j <= range_max):
                    break

                in_box_flag = True
                j -= 1

            if in_box_flag and (i - j) >= min_length:
                df.loc[j+1:i, 'in_box'] = True

            i = j