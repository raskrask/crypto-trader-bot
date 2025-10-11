import talib
import pandas as pd
import numpy as np
from datetime import datetime
from models.economic_data import EconomicData
from config.config_manager import get_config_manager

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
    "trade_signals_threshold": 0.02,  # 売買シグナルの閾値
    "trade_signals_window": 21,    # 売買シグナルの計算ウィンドウ
}

class FeatureDatasetModel:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.feature_columns = []

    def create_features(self, df):
        df = df.copy()
        df = self._add_technical_features(df)
        df = self._add_lag_features(df)
        df = self._add_return_signals(df)
        df.dropna(inplace=True)

        # ---- 説明変数と目的変数の分割 ----
        X = df[self.feature_columns]
        Y = df[['buy_signal', 'sell_signal']]

        return X, Y

#        y_buy = df[['target']]

#        return X, y_buy, None
#        y_buy = df[['buy_signal']].rename(columns={'buy_signal': 'target'})
#        y_sell = df[['sell_signal']].rename(columns={'sell_signal': 'target'})

#        return X, y_buy, y_sell

    def _add_technical_features(self, df):
        df = df.copy()
        market = self.config_data.get("market_symbol")
        open = df[f"open_{market}"]
        high = df[f"high_{market}"]
        low = df[f"low_{market}"]
        close = df[f"close_{market}"]
        volume = df[f"volume_{market}"]
        self.feature_columns.extend([f"open_{market}", f"high_{market}", f"low_{market}", f"close_{market}", f"volume_{market}"])

        # ---- (1) 移動平均 (SMA) ----
        for period in FEATURE_CONFIG["sma_periods"]:
            df[f"sma_{period}"] = talib.SMA(close, timeperiod=period)
            self.feature_columns.append(f"sma_{period}")
    
        df = self._add_ma_cross_signals(df)
        df = self._add_candle_signals(df, open, close)
        
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

    def _add_ma_cross_signals(self, df):
        """
        移動平均クロス（短期が長期を上抜け → 買いシグナル候補）
        売りシグナル：逆クロス OR 将来利回りが-閾値以下
        """
        for period_1 in FEATURE_CONFIG["sma_periods"]:
            for period_2 in FEATURE_CONFIG["sma_periods"]:
                if period_1 < period_2:
                    df_period_1 = df[f"sma_{period_1}"]
                    df_period_2 = df[f"sma_{period_2}"]
                    df[f"ma_cross_up_{period_1}_{period_2}"] = ((df_period_1 > df_period_2) & (df_period_1.shift(1) <= df_period_2.shift(1))).astype(int) 
                    df[f"ma_cross_down_{period_1}_{period_2}"] = ((df_period_1 < df_period_2) & (df_period_1.shift(1) >= df_period_2.shift(1))).astype(int) 
                    self.feature_columns.append(f"ma_cross_up_{period_1}_{period_2}")
                    self.feature_columns.append(f"ma_cross_down_{period_1}_{period_2}")
        return df

    def _add_candle_signals(self, df, open_, close):
        """陽線で5MAを上抜け、陰線で下抜けなどのシグナル"""
        if "sma_5" not in df.columns:
            return df  # 念のため

        sma5 = df["sma_5"]

        # 陽線で5MAを上抜け
        df["candle_cross_up_5"] = ((close > open_) & (close > sma5) & (open_ <= sma5)).astype(int)

        # 陰線で5MAを下抜け
        df["candle_cross_down_5"] = ((close < open_) & (close < sma5) & (open_ >= sma5)).astype(int)

        self.feature_columns += ["candle_cross_up_5", "candle_cross_down_5"]
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


    def _add_return_signals(self, df,
                            lag_days = 20, return_threshold = 0.03):
        """
        移動平均クロスと将来リターン閾値で買い・売りシグナルを作成する。
        
        Args:
            lag_days (int): 将来リターンを計算する日数
            return_threshold (float): 利回りの閾値（例: 0.03 = 3%）
        
        Returns:
            pd.DataFrame: シグナル列 'buy_signal', 'sell_signal' を追加したDataFrame
        """
        df = df.copy()

        market = self.config_data.get("market_symbol")
        df["max_close"] = df[f"close_{market}"].rolling(lag_days).max().shift(-lag_days)
        df["min_close"] = df[f"close_{market}"].rolling(lag_days).min().shift(-lag_days)
        df['buy_signal'] = 0
        df['sell_signal'] = 0

        df["max_return"] = df["max_close"] / df[f"close_{market}"]
        df["min_return"] = df["min_close"] / df[f"close_{market}"]
        df['buy_signal'] =  (df["max_return"] > (1+return_threshold)).astype(int) 
        df['sell_signal'] = (df["min_return"] < (1-return_threshold)).astype(int) 
        df.loc[(df['buy_signal'] == 1) & (df['sell_signal'] == 1), ['buy_signal','sell_signal']] = 0
        df.dropna(inplace=True)

        return df
