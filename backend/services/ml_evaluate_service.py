import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from sklearn.metrics import mean_squared_error, mean_absolute_error
from models.binance_fetcher import BinanceFetcher
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.min_max_scaler_processor import MinMaxScalerProcessor
from models.ensemble_model import EnsembleModel
from config.config_manager import get_config_manager
from utils.s3_helper import get_s3_helper
from config import constants

class MlEvaluteService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()

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

            self.fetcher = BinanceFetcher()
            self.crypto_data = CryptoTrainingDataset()
            self.feature_model = FeatureDatasetModel()
            self.scaler = MinMaxScalerProcessor()
            self.ensemble_model = EnsembleModel()

            # 予測結果
            raw_data = self.crypto_data.get_data()
            feature_data = self.feature_model.create_features(raw_data)
            X, _ = self.feature_model.select_features(feature_data)
            X, _ = self.scaler.transform(X)

            self.ensemble_model.load_model()
            y_pred = self.ensemble_model.predict(X)

            X, y_pred = self.scaler.inverse_transform(X, y_pred)
            y_pred = np.array(y_pred).ravel().tolist()
            target_lag_Y = self.config_data.get("target_lag_Y")


            # 過去のtimestampデータ
#            dates = raw_data["timestamp"].iloc[(len(y_pred)-target_lag_Y-1):].tolist()
            dates = raw_data["timestamp"].iloc[(target_lag_Y-len(y_pred)):].tolist()

            training_timeframe = self.config_data.get("training_timeframe")
            future_dates = [(dates[-1] + timedelta(minutes=training_timeframe * (i+1))) for i in range(target_lag_Y)]
            dates.extend(future_dates)
            print(f"raw_data.iloc2 = {len(dates)}")

            # 実際のBTC価格データ
            actual = raw_data["close_BTC_USDT"].iloc[(target_lag_Y-len(y_pred)):].tolist()
            actual.extend([-1] * target_lag_Y)



            # ゴールデンクロス用
#            y_pred = list(y_pred) if isinstance(y_pred, (list, np.ndarray)) else []
#            actual = list(actual) if isinstance(actual, (list, np.ndarray)) else []
#            y_pred_array = np.array(y_pred, dtype=np.float64)  # 数値型を明示
#            actual_array = np.array(actual, dtype=np.float64)  # 数値型を明示
#            y_pred = y_pred_array * actual_array
#            y_pred = y_pred.ravel().tolist()




            print(f"{len(raw_data)} {len(dates)} {len(actual)} {len(y_pred)} ")

            result = {
                "dates": dates,
                "actual": actual,
                "current_model": y_pred,
                "new_model": y_pred,
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

    def promote_model(self):
        """新しいモデルを本番環境に適用"""
        try:
            s3 = get_s3_helper()

            fld_stg = f"{constants.S3_FOLDER_MODEL}/staging"
            fld_prd = f"{constants.S3_FOLDER_MODEL}/production"
            arc_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            fld_arc = f"{constants.S3_FOLDER_MODEL}/archived/{arc_date}"

            s3.copy_s3_folder_recursive(fld_prd, fld_arc)
            s3.copy_s3_folder_recursive(fld_stg, fld_prd)
            return True
        except Exception as e:
            print(f"Model promotion failed: {e}")
            raise e