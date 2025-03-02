import talib
import pandas as pd
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
    ]
}

class FeatureDatasetModel:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.feature_columns = []

    def create_features(self, df):
        df = df.copy()
        df = self._add_technical_features(df)
        df = self._add_lag_features(df)
        df = self._add_economic_features(df)
        df.dropna(inplace=True)

        # ---- 説明変数と目的変数の分割 ----
        X = df[self.feature_columns]
        y = df["target"]

        return X, y

    def _add_technical_features(self, df):
        df = df.copy()
        market = self.config_data.get("market_symbol")
        open = df[f"open_{market}"]
        high = df[f"high_{market}"]
        low = df[f"low_{market}"]
        close = df[f"close_{market}"]
        volume = df[f"volume_{market}"]

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

        for lag in range(1, lag_days + 1):
            for col in self.feature_columns:
                lagged_features[f"{col}_lag{lag}"] = df[col].shift(lag)
                columns.append(f"{col}_lag{lag}")

        df = pd.concat([df, pd.DataFrame(lagged_features)], axis=1)
        self.feature_columns.extend(columns)

        # ---- 目的変数 (ターゲット) ----
        market = self.config_data.get("market_symbol")
        close = df[f"close_{market}"]
#        df["future_return"] = close.shift(-lag_days) / close - 1
#        df["target"] = (df["future_return"] > 0).astype(int)  # 上昇: 1, 下降: 0
        df["target"] = close.shift(-lag_days)

        return df

    def _add_economic_features(self, df):
        economic_data = EconomicData()
        economic_df = economic_data.get_economic_indicators(df["timestamp"][0])
        all_dates = pd.DataFrame({"timestamp": pd.date_range(start=economic_df["timestamp"].min(), 
                                                     end=economic_df["timestamp"].max(), freq="D")})
        economic_df = all_dates.merge(economic_df, on="timestamp", how="left")
        economic_df = economic_df.ffill()

        df = df.merge(economic_df, on="timestamp", how="left")

        economic_columns = [col for col in economic_df.columns if col != "timestamp"]
        self.feature_columns.extend(economic_columns)

        # 影響度がつよすぎるため重みをつける
        economic_df[economic_columns] = economic_df[economic_columns] * 0.001

        return df
