import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from models.binance_fetcher import BinanceFetcher
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.min_max_scaler_processor import MinMaxScalerProcessor
from models.ensemble_model import EnsembleModel

class MlEvaluteService:
    def __init__(self):
        self.fetcher = BinanceFetcher()
        self.crypto_data = CryptoTrainingDataset()
        self.feature_model = FeatureDatasetModel()
        self.scaler = MinMaxScalerProcessor()
        self.ensemble_model = EnsembleModel()

    def get_predictions(self):
        """過去データと予測結果を比較して評価"""
        try:
            # 過去の実際の価格データ
    #        past_data = self.fetcher.fetch_ohlcv("VITE/USDT", "1d", 30, 30)
    #        past_data2 = self.fetcher.fetch_ohlcv("BTC/USDT", "1d", 30, 30)

    #        return {
    #            "dates": past_data["timestamp"].tolist(),
    #            "actual": past_data["close"].tolist(),
    #            "current_model": past_data["close"].tolist(),
    #            "new_model": past_data.tolist(),
    #            "evaluation": {
    #                "current_model": {"mse": 1, "mae": 3},
    #                "new_model": {"mse": 2, "mae": 4}
    #            }
    #        }
            # 予測結果
            raw_data = self.crypto_data.get_data()
            feature_data = self.feature_model.create_features(raw_data)
            X = feature_data[self.feature_model.feature_columns]
            X, _ = self.scaler.transform(X)

            self.ensemble_model.load_model()
            y_pred = self.ensemble_model.predict(X)
            X, y_pred = self.scaler.inverse_transform(X, y_pred)


            l=len(raw_data["timestamp"].tolist())
            min=len(y_pred)
            X = X[:min]
            print(X.shape)

            aa = raw_data["timestamp"].tolist()[:min]
            bb = raw_data["close_BTC_USDT"].tolist()[:min]

            print(f"{l} {len(y_pred)} {len(X)} {len(aa)} {len(bb)}")

            flat_list = np.array(y_pred).ravel().tolist()

            result = {
                "dates": raw_data["timestamp"].tolist()[:min],
                "actual": raw_data["close_BTC_USDT"].tolist()[:min],
                "current_model": flat_list,
                "new_model": flat_list,
                "evaluation": {
                    "current_model": {"mse": 1, "mae": 2},
                    "new_model": {"mse": 3, "mae": 4}
                }
            }
            return result

    #        X_test = self.data_repo.get_recent_features()

    #        if X_test is None or len(X_test) == 0:
    #            raise ValueError("予測に必要なデータがありません")

            # モデルをロード
    #        current_model = self.model_repo.load_current_model()
    #        new_model = self.model_repo.load_new_model()

            # 予測を実行
    #        current_pred = current_model.predict(X_test)
    #        new_pred = new_model.predict(X_test)

            # 誤差を計算
            mse_current = mean_squared_error(past_data["close"], y_pred)
            mse_new = mean_squared_error(past_data["close"], y_pred)

            mae_current = mean_absolute_error(past_data["close"], y_pred)
            mae_new = mean_absolute_error(past_data["close"], y_pred)

            # 返却データを整理
            return {
                "dates": past_data["timestamp"].tolist(),
                "actual": past_data["close"].tolist(),
                "current_model": y_pred.tolist(),
                "new_model": y_pred.tolist(),
                "evaluation": {
                    "current_model": {"mse": mse_current, "mae": mae_current},
                    "new_model": {"mse": mse_new, "mae": mae_new}
                }
            }
    #    def predict(self, raw_data):
    #        """新しいデータを受け取って予測"""
    #        print("Generating features for new data...")
    #        feature_data = self.feature_model.create_features(raw_data)
    #
    #        X = feature_data[["sma_5", "bollinger_upper", "bollinger_lower", "rsi"]]
    #
    #        print("Predicting future prices...")
    #        predictions = self.ensemble_model.predict(X)
    #        return predictions
        except Exception as e:
            print(f"Prediction failed: {e}")
            raise e
