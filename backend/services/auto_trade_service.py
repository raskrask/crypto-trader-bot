import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.min_max_scaler_processor import MinMaxScalerProcessor
from models.ensemble_model import EnsembleModel
from models.exchanges.coincheck_api import CoinCheckAPI
from config.config_manager import get_config_manager
from config.settings import settings
from utils.s3_helper import get_s3_helper
from config import constants

class AutoTradeService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.s3 = get_s3_helper()
        self.market = self.config_data.get("market_symbol")
        self.confidence_threshold = 0.005


    def run(self):
        self.crypto_data = CryptoTrainingDataset()
        self.feature_model = FeatureDatasetModel()
        self.scaler = MinMaxScalerProcessor(stage="production")
        self.ensemble_model = EnsembleModel(stage="production")
        self.coincheck = CoinCheckAPI()

        predict = self._predict()
        trade = self._determine_trade_action(predict)
        self._execute_trade(trade)

        result = { "exchange":"coincheck", **predict, **trade }

        self._notify_slack(result)
        self._save_trade(result)

    def _predict(self):
        raw_data = self.crypto_data.get_data()
        feature_data = self.feature_model.create_features(raw_data)
        X, _ = self.feature_model.select_features(feature_data)
        X, _ = self.scaler.transform(X)

        self.ensemble_model.load_model()
        y_pred = self.ensemble_model.predict(X)
        _, y_pred = self.scaler.inverse_transform(X, y_pred)

        execution_date = datetime.now(timezone.utc)
        lag = self.config_data.get("target_lag_Y")
        frame = self.config_data.get("training_timeframe")
        prediction_date = self.crypto_data.end_date + timedelta(minutes=(lag*frame))
        execution_price = int(raw_data.iloc[-1][f"close_{self.market}"])
        predicted_price = int(y_pred[-1][0])

        result = {  
            "execution_date": execution_date.strftime("%Y-%m-%d %H:%M:%S"),
            "prediction_date": prediction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_price": execution_price,
            "predicted_price": predicted_price,
            "market": self.market,
        }
        return result

    def _determine_trade_action(self, predict):
        predicted_price = predict["predicted_price"]
        execution_price = predict["execution_price"]

        balance = self.coincheck.get_balance()
        books = self.coincheck.get_order_book()
        confidence = abs((predicted_price - execution_price) / execution_price)

        # 売買判断
        if confidence < self.confidence_threshold:  # 変動が小さい場合はHOLD
            prediction_label = "hold"
            price = float(self.coincheck.get_latest_rate(self.market)["rate"])
            amount = 0

        elif predicted_price > execution_price:
            prediction_label = "buy"
            amount = self.config_data.get("auto_trade_buy_amount")
            rate_info = self.coincheck.get_exchange_rate(self.market, "buy", amount)
            price = min(float(books["bids"][0][0]), float(rate_info["price"]))

            if  [1] < float(rate_info["price"]):
                prediction_label = "hold" # 資金不足
                amount = 0

        else:
            prediction_label = "sell"
            amount = self.config_data.get("auto_trade_sell_amount")
            rate_info = self.coincheck.get_exchange_rate(self.market, "sell", amount)
            price = max(float(books["asks"][0][0]), float(rate_info["price"]))
            avg_cost = self.coincheck.get_avg_cost() or 0
            if avg_cost > price or balance[0] < amount:
                prediction_label = "hold" # 損切りしない
                amount = 0

        return {
            "price": price,
            "amount": amount,
            "cost": amount * price,
            "confidence": confidence,
            "prediction_label": prediction_label
        }

    def _execute_trade(self, trade):
        if trade['prediction_label'] != 'hold':
            print(f"Executing trade: {trade}")
            self.coincheck.create_limit_order(trade["prediction_label"], trade["amount"], trade["price"])

    def _notify_slack(self, trade_result):
        if trade_result['prediction_label'] == 'hold':
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

    def _save_trade(self, result):
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        s3_key = f"{constants.S3_FOLDER_TRADE}/{self.market}_{date_str}.json"
        self.s3.save_json_to_s3(result, s3_key)

if __name__ == "__main__":
    me = AutoTradeService()

    me.crypto_data = CryptoTrainingDataset()
    me.feature_model = FeatureDatasetModel()
    me.scaler = MinMaxScalerProcessor(stage="production")
    me.ensemble_model = EnsembleModel(stage="production")
    me.coincheck = CoinCheckAPI()

    predict = me._predict()
    trade = me._determine_trade_action(predict)


    result = { "exchange":"coincheck", **predict, **trade }

    print(result)

    #me.run()