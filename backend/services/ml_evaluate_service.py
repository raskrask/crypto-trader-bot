import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from models.exchanges.binance_fetcher import BinanceFetcher
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.scalers.log_z_scaler_processor import LogZScalerProcessor
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
            self.crypto_data.start_date = self.crypto_data.end_date - relativedelta(months=12)

            raw_data = self.crypto_data.get_data()
#            feature_data = self.feature_model.create_features(raw_data)
#            X, _ = self.feature_model.select_features(feature_data)
            X, y  = self.feature_model.create_features(raw_data)

            # 予測結果(Staging)
            scaler_stg = LogZScalerProcessor()
            y_pred_buy_stg = self._predict(scaler_stg, EnsembleModel(), X, "buy_signal")
            y_pred_sell_stg = self._predict(scaler_stg, EnsembleModel(), X, "sell_signal")

            # 予測結果(Production)        
            try:
                scaler_prd = LogZScalerProcessor(stage="production")
                y_pred_buy_prd = self._predict(scaler_prd, EnsembleModel(stage="production"), X, "buy_signal")
                y_pred_sell_prd = self._predict(scaler_prd, EnsembleModel(stage="production"), X, "sell_signal")
            except Exception as e:
                y_pred_buy_prd = y_pred_buy_stg
                y_pred_sell_prd = y_pred_sell_stg

            # 実際の価格データ
            dates = raw_data["timestamp"].iloc[(-len(X)):].tolist()
            actual_buy_signal = y['buy_signal'].iloc[(-len(X)):].tolist()
            actual_sell_signal = y['sell_signal'].iloc[(-len(X)):].tolist()

            market = self.config_data.get("market_symbol")
            result = {
                "dates": dates,
                "price": X[f"close_{market}"].tolist(),
                "actual_buy_signal": actual_buy_signal,
                "actual_sell_signal": [-x for x in actual_sell_signal],
                "current_buy_model": y_pred_buy_prd,
                "current_sell_model": [-x for x in y_pred_sell_prd],
                "new_buy_model": y_pred_buy_stg,
                "new_sell_model": [-x for x in y_pred_sell_stg],
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
        
    def _predict(self, scaler, ensemble_model, X, type):
        X = scaler.transform(X)
        ensemble_model.load_model(type)
        y_pred = ensemble_model.predict(X)
        y_pred = np.array(y_pred).ravel().tolist()

        return y_pred
