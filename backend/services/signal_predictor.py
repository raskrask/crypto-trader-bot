import numpy as np
from datetime import datetime, timedelta, timezone
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.scalers.log_z_scaler_processor import LogZScalerProcessor
from models.ensemble_model import EnsembleModel
from utils.market_symbol import market_symbol
from config.constants import SIGNAL_BUY , SIGNAL_SELL, STAGE_PRODUCTION
from config.config_manager import get_config_manager

class SignalPredictor:
    def get_signals(self):
        # Dummy implementation for signal prediction
        return {"signal": "buy", "confidence": 0.95}
    
    def get_predict_signals(self):
        crypto_data = CryptoTrainingDataset()
        crypto_data.start_date = datetime.now(timezone.utc) - timedelta(days=90)
        crypto_data.end_date = datetime.now(timezone.utc)
        feature_model = FeatureDatasetModel()
        scaler = LogZScalerProcessor(stage=STAGE_PRODUCTION)

        model_buy = EnsembleModel(stage=STAGE_PRODUCTION)
        model_sell = EnsembleModel(stage=STAGE_PRODUCTION)

        raw_data = crypto_data.get_data()
        X = feature_model.create_features(raw_data) 
        X = scaler.transform(X)

        model_buy.load_model(SIGNAL_BUY)
        y_pred_buy = model_buy.predict(X)
        y_pred_buy = np.array(y_pred_buy).ravel()

        model_sell.load_model(SIGNAL_SELL)
        y_pred_sell = model_sell.predict(X)
        y_pred_sell = [-x for x in y_pred_sell]
        y_pred_sell = np.array(y_pred_sell).ravel()

        open = raw_data[market_symbol(prefix="open_")][-len(y_pred_buy):]
        close = raw_data[market_symbol(prefix="close_")][-len(y_pred_buy):]
        high = raw_data[market_symbol(prefix="high_")][-len(y_pred_buy):]
        low = raw_data[market_symbol(prefix="low_")][-len(y_pred_buy):]

        config_data = get_config_manager().get_config()
        target_buy_rate = config_data.get("target_buy_rate")
        target_sell_rate = config_data.get("target_sell_rate")
        predict_price = close * (1 + y_pred_buy * target_buy_rate + y_pred_sell * target_sell_rate)

        return {
            "buy": y_pred_buy.tolist(), 
            "sell": y_pred_sell.tolist(),
            "date": raw_data["timestamp"].tolist()[-len(y_pred_buy):],
            "open": open.tolist(),
            "close": close.tolist(),
            "high": high.tolist(),
            "low": low.tolist(),
            "predict_price": predict_price.tolist()
        }

