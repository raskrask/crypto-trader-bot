import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from models.exchanges.binance_fetcher import BinanceFetcher
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
            self.crypto_data = CryptoTrainingDataset()
            self.feature_model = FeatureDatasetModel()

            # 教師データを含まない過去の実際の価格データから予測
            #training_period_months = self.config_data.get("training_period_months")
            #self.crypto_data.end_date = self.crypto_data.end_date - relativedelta(months=3) # training_period_months
            self.crypto_data.start_date = self.crypto_data.end_date - relativedelta(months=3)

            raw_data = self.crypto_data.get_data()
            feature_data = self.feature_model.create_features(raw_data)
            X, _ = self.feature_model.select_features(feature_data)

            # 予測結果(Staging)
            scaler_stg = MinMaxScalerProcessor()
            ensemble_model_stg = EnsembleModel()
            y_pred_stg = self._predict(scaler_stg, ensemble_model_stg, X)

            # 予測結果(Production)
            scaler_prd = MinMaxScalerProcessor(stage="production")
            ensemble_model_prd = EnsembleModel(stage="production")
            y_pred_prd = self._predict(scaler_prd, ensemble_model_prd, X)

            # 日付ラベル
            target_lag_Y = self.config_data.get("target_lag_Y")
            training_timeframe = self.config_data.get("training_timeframe")
            dates = raw_data["timestamp"].iloc[(target_lag_Y-len(y_pred_stg)):].tolist()
            future_dates = [(dates[-1] + timedelta(minutes=training_timeframe * (i+1))) for i in range(target_lag_Y)]
            dates.extend(future_dates)

            # 実際の価格データ
            market = self.config_data.get("market_symbol")
            actual = raw_data[f"close_{market}"].iloc[(target_lag_Y-len(y_pred_stg)):].tolist()
            actual.extend([-1] * target_lag_Y)

            result = {
                "dates": dates,
                "actual": actual,
                "current_model": y_pred_prd,
                "new_model": y_pred_stg,
                "evaluation": {
                    "current_model": {"mse": 1, "mae": 2},
                    "new_model": {"mse": 3, "mae": 4}
                }
            }
            return result

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
        
    def _predict(self, scaler, ensemble_model, X):
        print(X)
        X, _ = scaler.transform(X)
        ensemble_model.load_model()
        y_pred = ensemble_model.predict(X)

        X, y_pred = scaler.inverse_transform(X, y_pred)
        y_pred = np.array(y_pred).ravel().tolist()

        return y_pred
