import talib
import pandas as pd
from config.config_manager import get_config_manager

class FeatureDatasetModel:
    def __init__(self):
        self.feature_columns = [ # 説明変数カラムリスト
            "sma_5","sma_10","sma_15","sma_20", "sma_50",
            "bollinger_upper","bollinger_upper10","bollinger_upper15","bollinger_upper20",
            "bollinger_lower","bollinger_lower10","bollinger_lower15","bollinger_lower20",
            "BB_upper", "BB_middle", "BB_lower",
            "rsi","OBV","RSI_14",
            "tr",
            "atr","atr5","atr10","atr15","atr20","ATR_14",
            "sma_10_lag1", "sma_50_lag1", "RSI_14_lag1", "BB_middle_lag1", "ATR_14_lag1", "OBV_lag1",
            "sma_10_lag2", "sma_50_lag2", "RSI_14_lag2", "BB_middle_lag2", "ATR_14_lag2", "OBV_lag2",
            "sma_10_lag3", "sma_50_lag3", "RSI_14_lag3", "BB_middle_lag3", "ATR_14_lag3", "OBV_lag3"
        ]  
        self.target_column = "target" #close_BTC_USDT"   # 目的変数カラム名
        self.config_data = get_config_manager().get_config()


    def create_features_NEW(self, df):
        df.set_index("timestamp", inplace=True)
        column_mapping = {"open_BTC_USDT":"open", "high_BTC_USDT":"high", "low_BTC_USDT":"low", "close_BTC_USDT":"close", "volume_BTC_USDT":"volume"}
        df = df.rename(columns=column_mapping)

        # テクニカル指標の計算
        df["SMA_10"] = talib.SMA(df["close"], timeperiod=10)
        df["SMA_50"] = talib.SMA(df["close"], timeperiod=50)
        df["RSI_14"] = talib.RSI(df["close"], timeperiod=14)
        df["BB_upper"], df["BB_middle"], df["BB_lower"] = talib.BBANDS(df["close"], timeperiod=20)
        df["ATR_14"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=14)
        df["OBV"] = talib.OBV(df["close"], df["volume"])

        # ラグ特徴量の作成（過去3日分）
        lag_features = ["SMA_10", "SMA_50", "RSI_14", "BB_middle", "ATR_14", "OBV"]
        for lag in range(1, 4):
            for feature in lag_features:
                df[f"{feature}_lag{lag}"] = df[feature].shift(lag)

        # 目的変数の作成（未来3日後のリターンがプラスかマイナスかを分類）
        df["future_return"] = df["close"].shift(-3) / df["close"] - 1
        df["target"] = (df["future_return"] > 0).astype(int)  # 1: 上昇, 0: 下降

        # 欠損値の除去
        df.dropna(inplace=True)

        # 説明変数と目的変数
        X = df.drop(columns=["close", "high", "low", "open", "volume", "future_return", "target"])
        y = df["target"]

        return X, y

    def create_features(self, df):
        """トレーニングデータら特徴量を作成"""
        window_bb = self.config_data.get("feature_lag_X_BB")
        window_atr = self.config_data.get("feature_lag_X_ATR")

        # 移動平均 (SMA) を作成
        df["sma_5"] = df["close_BTC_USDT"].rolling(window=window_bb).mean()
        df["sma_10"] = df["close_BTC_USDT"].rolling(window=10).mean()
        df["sma_15"] = df["close_BTC_USDT"].rolling(window=15).mean()
        df["sma_20"] = df["close_BTC_USDT"].rolling(window=20).mean()
        df["sma_50"] = df["close_BTC_USDT"].rolling(window=50).mean()

        # ボリンジャーバンド
        df["bollinger_upper"] = df["sma_5"] + 2 * df["close_BTC_USDT"].rolling(window=window_bb).std()
        df["bollinger_lower"] = df["sma_5"] - 2 * df["close_BTC_USDT"].rolling(window=window_bb).std()

        df["BB_upper"], df["BB_middle"], df["BB_lower"] = talib.BBANDS(df["close_BTC_USDT"], timeperiod=20)


        df["bollinger_upper10"] = df["sma_10"] + 2 * df["close_BTC_USDT"].rolling(window=10).std()
        df["bollinger_lower10"] = df["sma_10"] - 2 * df["close_BTC_USDT"].rolling(window=10).std()
        df["bollinger_upper15"] = df["sma_15"] + 2 * df["close_BTC_USDT"].rolling(window=15).std()
        df["bollinger_lower15"] = df["sma_15"] - 2 * df["close_BTC_USDT"].rolling(window=15).std()
        df["bollinger_upper20"] = df["sma_20"] + 2 * df["close_BTC_USDT"].rolling(window=20).std()
        df["bollinger_lower20"] = df["sma_20"] - 2 * df["close_BTC_USDT"].rolling(window=20).std()

        df["OBV"] = talib.OBV(df["close_BTC_USDT"], df["volume_BTC_USDT"])


        # RSI の計算（簡易的）
        df["rsi"] = 100 - (100 / (1 + (df["high_BTC_USDT"] / df["low_BTC_USDT"])))
        df["RSI_14"] = talib.RSI(df["close_BTC_USDT"], timeperiod=14)

        # ATR (Average True Range) の計算
        df["tr"] = df[["high_BTC_USDT", "low_BTC_USDT", "close_BTC_USDT"]].max(axis=1) - df[["high_BTC_USDT", "low_BTC_USDT", "close_BTC_USDT"]].min(axis=1)
        df["atr"] = df["tr"].rolling(window=window_atr).mean()
        df["ATR_14"] = talib.ATR(df["high_BTC_USDT"], df["low_BTC_USDT"], df["close_BTC_USDT"], timeperiod=14)

        df["atr5"] = df["tr"].rolling(window=5).mean()
        df["atr10"] = df["tr"].rolling(window=10).mean()
        df["atr15"] = df["tr"].rolling(window=15).mean()
        df["atr20"] = df["tr"].rolling(window=20).mean()

        lag_features = ["sma_10", "sma_50", "RSI_14", "BB_middle", "ATR_14", "OBV"]
        for lag in range(1, 4):
            for feature in lag_features:
                df[f"{feature}_lag{lag}"] = df[feature].shift(lag)


        return df.dropna()

    def select_features(self, df):
        X = df[self.feature_columns]
        if self.target_column in df.columns:
            return X, df[self.target_column]

        return X, None

    def select_lagged_features(self, df):
        """
        未来 `target_lag_Y` 足の目的変数に移動した特徴量を返却する。

        検討中
        ① SMA5の未来変動を予測	SMA5の上昇/下降を分類問題にする
        ② SMAクロスを活用	短期SMAと長期SMAのクロスを見る
        ③ ボラティリティを考慮	ATRやボリンジャーバンドを特徴量に加える

        """
        target_lag_Y = self.config_data.get("target_lag_Y")

#        #検証中
        df = df.copy()
        df[self.target_column] = df["close_BTC_USDT"].shift(-target_lag_Y)
        df = df.dropna()
        X, y = self.select_features(df)

#        X = df[self.feature_columns]
#        y = df["target"]

        return X, y




        X, y = self.select_features(df)
#        y = y.sort_index(ascending=False)
        #y = y.rolling(window=target_lag_Y).mean().shift(-(target_lag_Y-1)).dropna()

        # 終値直接指定
        y = y.shift(-target_lag_Y).dropna()

#        # 短期SMAが長期SMAを上抜ける（ゴールデンクロス）
#        df_short = y.rolling(window=(target_lag_Y//2)).mean()
#        df_long = y.rolling(window=target_lag_Y).mean()
#        y = (df_short > df_long).astype(int)


#        y = y.sort_index(ascending=True)
#        y = y.dropna()
        y = y.iloc[target_lag_Y:]

        X = X.iloc[-len(y):]


        return X, y


        # 説明変数をシフト
        X = X[:-target_lag_Y]  

        # `rolling()` の適用時に `min_periods=1` を指定して NaN の発生を抑える
        y = y.rolling(window=target_lag_Y, min_periods=1).mean()

        # `dropna()` で `y` が短くなるので、 `X` を `y` の長さに合わせる
        y = y.dropna()
        X = X.iloc[-len(y):]  # `y` の行数に `X` を合わせる

        return X, y

    def create_features_(self, df):
        open = df['op']
        high = df['hi']
        low = df['lo']
        close = df['cl']
        volume = df['volume']
        
        orig_columns = df.columns

        hilo = (df['hi'] + df['lo']) / 2
        # 価格(hilo または close)を引いた後、価格(close)で割ることで標準化
        df['BBANDS_upperband'], df['BBANDS_middleband'], df['BBANDS_lowerband'] = talib.BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        df['BBANDS_upperband'] = (df['BBANDS_upperband'] - hilo) / close
        df['BBANDS_middleband'] = (df['BBANDS_middleband'] - hilo) / close
        df['BBANDS_lowerband'] = (df['BBANDS_lowerband'] - hilo) / close
        df['DEMA'] = (talib.DEMA(close, timeperiod=30) - hilo) / close
        df['EMA'] = (talib.EMA(close, timeperiod=30) - hilo) / close
        df['HT_TRENDLINE'] = (talib.HT_TRENDLINE(close) - hilo) / close
        df['KAMA'] = (talib.KAMA(close, timeperiod=30) - hilo) / close
        df['MA'] = (talib.MA(close, timeperiod=30, matype=0) - hilo) / close
        df['MIDPOINT'] = (talib.MIDPOINT(close, timeperiod=14) - hilo) / close
        df['SMA'] = (talib.SMA(close, timeperiod=30) - hilo) / close
        df['T3'] = (talib.T3(close, timeperiod=5, vfactor=0) - hilo) / close
        df['TEMA'] = (talib.TEMA(close, timeperiod=30) - hilo) / close
        df['TRIMA'] = (talib.TRIMA(close, timeperiod=30) - hilo) / close
        df['WMA'] = (talib.WMA(close, timeperiod=30) - hilo) / close
        df['LINEARREG'] = (talib.LINEARREG(close, timeperiod=14) - close) / close
        df['LINEARREG_INTERCEPT'] = (talib.LINEARREG_INTERCEPT(close, timeperiod=14) - close) / close


        # 価格(close)で割ることで標準化
        df['AD'] = talib.AD(high, low, close, volume) / close
        df['ADOSC'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10) / close
        df['APO'] = talib.APO(close, fastperiod=12, slowperiod=26, matype=0) / close
        df['HT_PHASOR_inphase'], df['HT_PHASOR_quadrature'] = talib.HT_PHASOR(close)
        df['HT_PHASOR_inphase'] /= close
        df['HT_PHASOR_quadrature'] /= close
        df['LINEARREG_SLOPE'] = talib.LINEARREG_SLOPE(close, timeperiod=14) / close
        df['MACD_macd'], df['MACD_macdsignal'], df['MACD_macdhist'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD_macd'] /= close
        df['MACD_macdsignal'] /= close
        df['MACD_macdhist'] /= close
        df['MINUS_DM'] = talib.MINUS_DM(high, low, timeperiod=14) / close
        df['MOM'] = talib.MOM(close, timeperiod=10) / close
        df['OBV'] = talib.OBV(close, volume) / close
        df['PLUS_DM'] = talib.PLUS_DM(high, low, timeperiod=14) / close
        df['STDDEV'] = talib.STDDEV(close, timeperiod=5, nbdev=1) / close
        df['TRANGE'] = talib.TRANGE(high, low, close) / close


        df['ADX'] = talib.ADX(high, low, close, timeperiod=14)
        df['ADXR'] = talib.ADXR(high, low, close, timeperiod=14)
        df['AROON_aroondown'], df['AROON_aroonup'] = talib.AROON(high, low, timeperiod=14)
        df['AROONOSC'] = talib.AROONOSC(high, low, timeperiod=14)
        df['BOP'] = talib.BOP(open, high, low, close)
        df['CCI'] = talib.CCI(high, low, close, timeperiod=14)
        df['DX'] = talib.DX(high, low, close, timeperiod=14)
        # skip MACDEXT MACDFIX たぶん同じなので
        df['MFI'] = talib.MFI(high, low, close, volume, timeperiod=14)
        df['MINUS_DI'] = talib.MINUS_DI(high, low, close, timeperiod=14)
        df['PLUS_DI'] = talib.PLUS_DI(high, low, close, timeperiod=14)
        df['RSI'] = talib.RSI(close, timeperiod=14)
        df['STOCH_slowk'], df['STOCH_slowd'] = talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df['STOCHF_fastk'], df['STOCHF_fastd'] = talib.STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0)
        df['STOCHRSI_fastk'], df['STOCHRSI_fastd'] = talib.STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        df['TRIX'] = talib.TRIX(close, timeperiod=30)
        df['ULTOSC'] = talib.ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28)
        df['WILLR'] = talib.WILLR(high, low, close, timeperiod=14)

        df['ATR'] = talib.ATR(high, low, close, timeperiod=14)
        df['NATR'] = talib.NATR(high, low, close, timeperiod=14)

        df['HT_DCPERIOD'] = talib.HT_DCPERIOD(close)
        df['HT_DCPHASE'] = talib.HT_DCPHASE(close)
        df['HT_SINE_sine'], df['HT_SINE_leadsine'] = talib.HT_SINE(close)
        df['HT_TRENDMODE'] = talib.HT_TRENDMODE(close)

        df['BETA'] = talib.BETA(high, low, timeperiod=5)
        df['CORREL'] = talib.CORREL(high, low, timeperiod=30)

        df['LINEARREG_ANGLE'] = talib.LINEARREG_ANGLE(close, timeperiod=14)
        return df