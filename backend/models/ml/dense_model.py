import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from .ml_model_base import MLModelBase


class DenseModel(MLModelBase):
    def __init__(self, learning_rate=0.001):
        super().__init__()
        self.model_type = "dense"
        self.learning_rate = learning_rate
        #self.model = self._build_model()
    

    def train(self, X_train, y_train, epochs=30, batch_size=32):
        """ Dense モデルの学習 """
        self.model = self._build_model(X_train.shape[1])

        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)

    def evaluate(self, X_test, y_test):
        """ Denseモデルの評価 """
        # **評価**
        result = self.model.evaluate(X_test, y_test, verbose=1)
        return {
            "loss": result[0],
            "mae": result[1]
        }

    def predict(self, X_test):
        """ Dense モデルでの予測 """

        # **予測**
        predictions = self.model.predict(X_test)
        predictions = np.array(predictions).reshape(-1)
        # **スケールを元に戻す**
#        predictions = self.scaler_y.inverse_transform(predictions_scaled.reshape(-1, 1))

        return predictions


    def _build_model(self, feature_dim):
        """LSTM モデルの構築"""
        model = Sequential([
            Input(shape=(feature_dim,)),
            Dense(128, activation="relu"),
            Dropout(0.2),
            Dense(64, activation="relu"),
            Dense(1, activation="sigmoid")
        ])
        model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def _export_model(self, path):
        """モデルを保存"""
        save_model(self.model, path)

    def _import_model(self, path):
        """モデルをロード"""
        self.model = load_model(path)

    def _get_model_filename(self):
        return f"{self.model_type}_model.keras"

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