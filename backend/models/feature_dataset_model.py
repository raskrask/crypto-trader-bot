import talib
import pandas as pd
import numpy as np
from datetime import datetime
from models.economic_data import EconomicData
from config.config_manager import get_config_manager
from config.constants import SIGNAL_BUY , SIGNAL_SELL
from utils.market_symbol import market_symbol
from models.swing_trade_strategy import SwingTradeStrategy

FEATURE_CONFIG = {
    "sma_periods": [5, 10, 15, 20, 50],  # 移動平均
    "bollinger_periods": [10, 15, 20],   # ボリンジャーバンド
    "atr_periods": [5, 10, 15, 20],      # ATR
    "rsi_period": 14,                    # RSI
    "macd_fast": 12,                      # MACD fast period
    "macd_slow": 26,                      # MACD slow period
    "macd_signal": 9,                      # MACD signal period
    "lag_days": 3,                         # 過去データのラグ数
    "use_features": [                      # 使用する特徴量
        "SMA", "RSI", "ATR", "BOLL", "OBV", "MACD", "STOCH"
    ],
}

class FeatureDatasetModel:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.feature_columns = []

    def create_features(self, df):
        df = df.copy()
        df = self._add_technical_features(df)
        df = self._add_lag_features(df)

        strategy = SwingTradeStrategy(df)
        self.feature_columns += strategy.trend_following()
        df = strategy.data

        df.dropna(inplace=True)

        return df[self.feature_columns]

    def create_targets(self, df):
        df = df.copy()
        df = self._add_return_signals(df)
        df.dropna(inplace=True)

        return df[[SIGNAL_BUY, SIGNAL_SELL]]

    def prepare_dataset(self, df):
        df = df.copy()
        df = self._add_technical_features(df)
        df = self._add_lag_features(df)

        strategy = SwingTradeStrategy(df)
        self.feature_columns += strategy.trend_following()
        df = strategy.data

        df = self._add_return_signals(df)
        df.dropna(inplace=True)

        # ---- 説明変数と目的変数の分割 ----
        X = df[self.feature_columns]
        Y = df[[SIGNAL_BUY, SIGNAL_SELL]]

        return X, Y


    def _add_technical_features(self, df):
        df = df.copy()
        keys = ["open", "high", "low", "close", "volume"]
        ohlcv = {k: df[market_symbol(prefix=f"{k}_")] for k in keys}
        open, high, low, close, volume = (
            ohlcv["open"], ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"]
        )
        self.feature_columns.extend([market_symbol(prefix=f"{k}_") for k in keys])

        # ---- (1) 移動平均 (SMA) ----
        for period in FEATURE_CONFIG["sma_periods"]:
            df[f"sma_{period}"] = talib.SMA(close, timeperiod=period)
            self.feature_columns.append(f"sma_{period}")

        # ---- (2) ボリンジャーバンド (BOLL) ----
        for period in FEATURE_CONFIG["bollinger_periods"]:
            upper, middle, lower = talib.BBANDS(close, timeperiod=period)
            df[f"bollinger_upper{period}"] = upper
            df[f"bollinger_middle{period}"] = middle
            df[f"bollinger_lower{period}"] = lower
            self.feature_columns.extend([f"bollinger_upper{period}", f"bollinger_middle{period}", f"bollinger_lower{period}"])

        # ---- (3) ATR (Average True Range) ----
        for period in FEATURE_CONFIG["atr_periods"]:
            df[f"atr{period}"] = talib.ATR(high, low, close, timeperiod=period)
            self.feature_columns.append(f"atr{period}")

        # ---- (4) RSI (Relative Strength Index) ----
        rsi_period = FEATURE_CONFIG["rsi_period"]
        df["RSI"] = talib.RSI(close, timeperiod=rsi_period)
        self.feature_columns.append("RSI")

        # ---- (5) OBV (On-Balance Volume) ----
        df["OBV"] = talib.OBV(close, volume)
        self.feature_columns.append("OBV")

        # ---- (6) MACD ----
        macd_fast = FEATURE_CONFIG["macd_fast"]
        macd_slow = FEATURE_CONFIG["macd_slow"]
        macd_signal = FEATURE_CONFIG["macd_signal"]
        df["MACD"], df["MACD_signal"], df["MACD_hist"] = talib.MACD(close, fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal)
        self.feature_columns.extend(["MACD", "MACD_signal", "MACD_hist"])

        # ---- (7) ストキャスティクス (Stochastic) ----
        df["STOCH_k"], df["STOCH_d"] = talib.STOCH(high, low, close)
        self.feature_columns.extend(["STOCH_k", "STOCH_d"])

        return df


    def _add_lag_features(self, df):

        lagged_features = {}
        columns = []
        lag_days = FEATURE_CONFIG["lag_days"]
        market = self.config_data.get("market_symbol")

        for lag in range(1, lag_days + 1):
            for col in [f"open_{market}", f"high_{market}", f"low_{market}", f"close_{market}", f"volume_{market}"]:
                lagged_features[f"{col}_lag{lag}"] = df[col].shift(lag)
                columns.append(f"{col}_lag{lag}")

        df = pd.concat([df, pd.DataFrame(lagged_features)], axis=1)
        self.feature_columns.extend(columns)

        # ---- 旧目的変数 (ターゲット) ----
        market = self.config_data.get("market_symbol")
        close = df[f"close_{market}"]
#        df["future_return"] = close.shift(-lag_days) / close - 1
#        df["target"] = (df["future_return"] > 0).astype(int)  # 上昇: 1, 下降: 0
#        df["target"] = close.shift(-lag_days)

        return df


    def _add_return_signals(self, df):
        """
        移動平均クロスと将来リターン閾値で買い・売りシグナルを作成する。
        
        Returns:
            pd.DataFrame: シグナル列 'buy_signal', 'sell_signal' を追加したDataFrame
        """
        df = df.copy()
        close = df[market_symbol(prefix="close_")]
        target_buy_term = self.config_data.get("target_buy_term")
        target_buy_rate = self.config_data.get("target_buy_rate")
        target_sell_term = self.config_data.get("target_sell_term")
        target_sell_rate = self.config_data.get("target_sell_rate")
        df["max_close"] = close.rolling(target_buy_term).max().shift(-target_buy_term)
        df["min_close"] = close.rolling(target_sell_term).min().shift(-target_sell_term)

        df["max_return"] = df["max_close"] / close
        df["min_return"] = df["min_close"] / close
        df[SIGNAL_BUY] =  (df["max_return"] > (1+target_buy_rate)).astype(int) 
        df[SIGNAL_SELL] = (df["min_return"] < (1-target_sell_rate)).astype(int) 
        df.loc[(df[SIGNAL_BUY] == 1) & (df[SIGNAL_SELL] == 1), [SIGNAL_BUY, SIGNAL_SELL]] = 0

        return df
