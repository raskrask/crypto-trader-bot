import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.min_max_scaler_processor import MinMaxScalerProcessor
from models.ensemble_model import EnsembleModel
from config.config_manager import get_config_manager
from config.settings import settings
from utils.s3_helper import get_s3_helper
from config import constants

class AutoTradeService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.s3 = get_s3_helper()

    def run(self):
        self.crypto_data = CryptoTrainingDataset()
        self.feature_model = FeatureDatasetModel()
        self.scaler = MinMaxScalerProcessor(stage="production")
        self.ensemble_model = EnsembleModel(stage="production")

        predict_result = self._predict()
        trade_result = self._execute_trade()
        self._notify_slack(predict_result)

    def _predict(self):
        raw_data = self.crypto_data.get_data()
        feature_data = self.feature_model.create_features(raw_data)
        X, _ = self.feature_model.select_features(feature_data)
        X, _ = self.scaler.transform(X)

        self.ensemble_model.load_model()
        y_pred = self.ensemble_model.predict(X)
        _, y_pred = self.scaler.inverse_transform(X, y_pred)

        market = "BTC_USDT"
        execution_date = datetime.now(timezone.utc)
        lag = self.config_data.get("target_lag_Y")
        frame = self.config_data.get("training_timeframe")
        prediction_date = self.crypto_data.end_date + timedelta(minutes=(lag*frame))
        execution_price = int(raw_data.iloc[-1]["close_BTC_USDT"])
        predicted_price = int(y_pred[-1][0])

        # 売買判断
        trade = self._determine_trade_action(predicted_price, execution_price)

        result = {  
            "execution_date": execution_date.strftime("%Y-%m-%d %H:%M:%S"),
            "prediction_date": prediction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_price": execution_price,
            "predicted_price": predicted_price,
            "market": market,
            "prediction_label": trade["prediction_label"],
            "confidence": trade["confidence"]
        }
        s3_key = f"{constants.S3_FOLDER_TRADE}/{market}_{execution_date.strftime('%Y-%m-%d')}.json"
        self.s3.save_json_to_s3(result, s3_key)
        return result

    def _determine_trade_action(self, predicted_price, execution_price):
        """
        予測価格、実行価格を元にスプレッドを考慮した売買判断を行う。
        """
        spread_rate = 0.05  # 5%のスプレッド

        # 「買い」ならスプレッド上乗せ、「売り」ならスプレッド減算
        if predicted_price > execution_price:
            adjusted_execution_price = execution_price * (1 + spread_rate)  # 5%上乗せ
        else:
            adjusted_execution_price = execution_price * (1 - spread_rate)  # 5%減算

        # スプレッド適用後のconfidence計算
        confidence = abs((predicted_price + adjusted_execution_price) / adjusted_execution_price)

        # 売買判断
        if confidence < 0.01:  # 変動が小さい場合はHOLD
            prediction_label = "HOLD"
        elif predicted_price > adjusted_execution_price:  # 予測価格が調整後価格を上回るならBUY
            prediction_label = "BUY"
        else:
            prediction_label = "SELL"

        return {
            "adjusted_execution_price": adjusted_execution_price,
            "confidence": confidence,
            "prediction_label": prediction_label
        }

    def _execute_trade(self):
        pass

    def _notify_slack(self, trade_result):
        if trade_result['prediction_label'] == 'HOLD':
            message = (
                f"⚠ 取引を実行しませんでした。\n"
                f"*予測日:* {trade_result['prediction_date']}\n"
                f"*実行価格:* {trade_result['execution_price']}\n"
                f"*予測価格:* {trade_result['predicted_price']}\n"
                f"*信頼度:* {trade_result['confidence']:.2f}\n"
            )
        else:
            message = (
                f"🚀 *検証中　自動取引実行*🚀\n"
                f"*市場:* {trade_result['market']}\n"
                f"*注文種別:* {trade_result['prediction_label']}\n"
                f"*予測日:* {trade_result['execution_date']}\n"
                f"*実行価格:* {trade_result['execution_price']}\n"
                f"*予測価格:* {trade_result['predicted_price']}\n"
                f"*信頼度:* {trade_result['confidence']:.2f}"
            )

        if settings.DEBUG:
            message = f"[Develop] {message}"
        payload = {"text": message}
        headers = {"Content-Type": "application/json"}
    
        requests.post(settings.SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
