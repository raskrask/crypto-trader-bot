import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from .ml_model_base import MLModelBase
from utils.data_processing import generate_sequences


class LSTMModel(MLModelBase):
    def __init__(self, sequence_length=30, units=50, learning_rate=0.001, target_column=0):
        super().__init__(sequence_model=True)
        self.model_type = "lstm"
        self.sequence_length = sequence_length
        self.units = units
        self.learning_rate = learning_rate
        self.target_column = target_column
#        self.scaler_X = MinMaxScaler(feature_range=(0, 1))  # 特徴量スケーラー
#        self.scaler_y = MinMaxScaler(feature_range=(0, 1))  # 目的変数スケーラー
#        self.scaler_X = MinMaxScaler()  # 全ての特徴量に適用
#        self.scaler_y = MinMaxScaler()
        self.model = self._build_model()
    


    def train(self, X_train, y_train, epochs=30, batch_size=32):
        """ LSTM モデルの学習 """
        # **DataFrame を numpy に変換**
#        if isinstance(X_train, pd.DataFrame):
#            X_train = X_train.to_numpy()
#        if isinstance(y_train, pd.Series):
#            y_train = y_train.to_numpy()

        # **スケーリング (3D ではなく 2D に適用)**
 #       num_samples, num_features = X_train.shape
 #       X_train_scaled = self.scaler_X.fit_transform(X_train.reshape(num_samples, -1))  # 2D にする
 #       y_train_scaled = self.scaler_y.fit_transform(y_train.reshape(-1, 1))  # 2D にする

        # **シーケンス変換**
        X_train_lstm, y_train_lstm = generate_sequences(X_train, self.sequence_length, self.target_column)
        X_train_lstm = X_train_lstm.reshape(X_train_lstm.shape[0], self.sequence_length, X_train_lstm.shape[-1])

        print(f"✅ Debug: X_train_lstm.shape = {X_train_lstm.shape}, y_train_lstm.shape = {y_train_lstm.shape}")

        # **モデルの学習**
        self.model.fit(X_train_lstm, y_train_lstm, epochs=epochs, batch_size=batch_size, verbose=1)

    def evaluate(self, X_test, y_test):
        """ モデルの評価 """
        # **DataFrame を numpy に変換**
#        if isinstance(X_test, pd.DataFrame):
#            X_test = X_test.to_numpy()
#        if isinstance(y_test, pd.Series):
#            y_test = y_test.to_numpy()

        # **スケーリング適用**
 #       num_samples, num_features = X_test.shape
 #       X_test_scaled = self.scaler_X.transform(X_test.reshape(num_samples, -1))  # 2D にする
 #       y_test_scaled = self.scaler_y.transform(y_test.reshape(-1, 1))  # 2D にする

        # **シーケンス変換**
        X_test_lstm, y_test_lstm = generate_sequences(X_test, self.sequence_length, self.target_column)
        X_test_lstm = X_test_lstm.reshape(X_test_lstm.shape[0], self.sequence_length, X_test_lstm.shape[-1])

        print(f"✅ Debug: X_test_lstm.shape = {X_test_lstm.shape}, y_test_lstm.shape = {y_test_lstm.shape}")

        # **評価**
        result = self.model.evaluate(X_test_lstm, y_test_lstm, verbose=1)
        return {
            "loss": result[0],
            "mae": result[1]
        }

    def predict(self, X_test):
        """ LSTM モデルでの予測 """
        # **DataFrame を numpy に変換**
#        if isinstance(X_test, pd.DataFrame):
#            X_test = X_test.to_numpy()

        # **スケーリング適用**
 #       num_samples, num_features = X_test.shape
 #       X_test_scaled = self.scaler_X.transform(X_test.reshape(num_samples, -1))  # 2D にする

        # **シーケンス変換**
        X_test_lstm, _ = generate_sequences(X_test, self.sequence_length, self.target_column)
        X_test_lstm = X_test_lstm.reshape(X_test_lstm.shape[0], self.sequence_length, X_test_lstm.shape[-1])

        print(f"✅ Debug: X_test_lstm.shape = {X_test_lstm.shape}")

        # **予測**
        predictions = self.model.predict(X_test_lstm)

        # **スケールを元に戻す**
#        predictions = self.scaler_y.inverse_transform(predictions_scaled.reshape(-1, 1))

        return predictions


    def _build_model(self):
        """LSTM モデルの構築"""
        model = Sequential([
            Input(shape=(self.sequence_length, 6)),
            LSTM(128, return_sequences=True),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='mse', metrics=['mae'])
        return model

    def _save_model(self, path):
        """モデルを保存"""
        save_model(self.model, path)

    def _load_model(self, path):
        """モデルをロード"""
        self.model = load_model(path)

    def _get_model_filename(self):
        return f"{self.model_type}_model.keras"

    def evaluate(self, X_test, y_test):
        """LSTM モデルの評価"""
        # ** スケーリング（シーケンス化する前）**
#        X_test_scaled = self.scaler_X.transform(X_test)
#        y_test_scaled = self.scaler_y.transform(y_test.reshape(-1, 1))

        # ** シーケンスデータを生成 **
        X_test_lstm, y_test_lstm = generate_sequences(X_test, self.sequence_length, self.target_column)

        # ** reshape（(サンプル数, シーケンス長, 特徴量数)）**
        X_test_lstm = X_test_lstm.reshape(X_test_lstm.shape[0], self.sequence_length, X_test_lstm.shape[2])

        # ** 評価実行 **
        result = self.model.evaluate(X_test_lstm, y_test_lstm, verbose=1)
        return {
            "loss": result[0] if isinstance(result, (list, tuple)) else result, 
            "mae": result[1] if isinstance(result, (list, tuple)) else 0.0
        }

    def _build_model(self):
        """LSTM モデルの構築"""
        model = Sequential([
            Input(shape=(self.sequence_length, 6)),
            LSTM(128, return_sequences=True),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='mse', metrics=['mae'])
        return model

    def suggest_hyperparams(self, trial):
        """Optuna でのハイパーパラメータ設定"""
        return {
            "units": trial.suggest_int("units", 50, 200),
            "learning_rate": trial.suggest_float("learning_rate", 0.0001, 0.01),
            "batch_size": trial.suggest_int("batch_size", 16, 64),
            "epochs": trial.suggest_int("epochs", 10, 50),
        }

    def set_hyperparams(self, params):
        """最適化されたハイパーパラメータを適用"""
        self.units = params["units"]
        self.learning_rate = params["learning_rate"]
        self.model = self._build_model()

    def get_feature_importance(self, X_train):
        return None