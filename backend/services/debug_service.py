import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from models.exchanges.binance_fetcher import BinanceFetcher
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.scalers.log_z_scaler_processor import LogZScalerProcessor
from models.ensemble_model import EnsembleModel
from models.ml.lgbm_classifier_model import LgbmClassifierModel
from models.ml.lstm_model import LSTMModel
from models.evaluator import Evaluator
from config.config_manager import get_config_manager
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from utils.s3_helper import get_s3_helper
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from utils.data_processing import generate_sequences
from config.constants import SIGNAL_BUY

class DebugService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()

    def do_debug(self):
        # ------------------------- ML Pipeline -------------------------

        crypto_data = CryptoTrainingDataset()
        crypto_data.markets= ['BTC/JPY']
        crypto_data.start_date = datetime.now(timezone.utc) - timedelta(days=60)
        raw_data = crypto_data.get_data()

        feature_model = FeatureDatasetModel()
        X, y = feature_model.prepare_dataset(raw_data)
        print("--------------")
        print(raw_data.shape)
        print(X.head())
        print(X.tail())
        print(y.head()) 
        print(y.tail())
        print("--------------")
        #X = X[["open_btc_jpy", "high_btc_jpy", "low_btc_jpy", "close_btc_jpy", "volume_btc_jpy", "sma_5", "sma_20", "ma_cross_up_5_10"]]
        y = y[[SIGNAL_BUY]]

        scaler = LogZScalerProcessor()
        X = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=True)

        model = EnsembleModel()
        model.train(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred = pd.DataFrame(y_pred, columns=[SIGNAL_BUY], index=X_test.index)

        importance = model.get_feature_importance(X_test)
        eval_results = Evaluator().evaluate(y_test, y_pred)
        score = accuracy_score(y_test, y_pred.round())
        print(y_test.shape, y_pred.shape)
        print("Accuracy:", score)

        # ------------------------- ML Evaluate -------------------------

        crypto_data.start_date = crypto_data.end_date - relativedelta(months=12)
        raw_data = crypto_data.get_data()

        feature_model = FeatureDatasetModel()
        X, y  = feature_model.prepare_dataset(raw_data)
        y = y[[SIGNAL_BUY]]
        X = scaler.transform(X)
        y_pred = model.predict(X)
        y_pred = pd.DataFrame(y_pred, columns=[SIGNAL_BUY], index=X.index)
        print(y.shape, y_pred.shape)
        score = accuracy_score(y, y_pred.round())
        print("Accuracy:", score)

        result = { "accuracy": score, "importance": importance, "eval_results": eval_results }
        return jsonable_encoder(result)

