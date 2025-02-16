import numpy as np
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.min_max_scaler_processor import MinMaxScalerProcessor
from models.ensemble_model import EnsembleModel
from models.evaluator import Evaluator
from sklearn.model_selection import train_test_split
from config.config_manager import get_config_manager

class MlPipelineService:

    def __init__(self):
        self.crypto_data = CryptoTrainingDataset()
        self.feature_model = FeatureDatasetModel()
        self.scaler = MinMaxScalerProcessor()
        self.ensemble_model = EnsembleModel()
        self.evaluator = Evaluator()
        self.training_status = {"progress": 0, "status": "Not started", "result": None}
        self.config_data = get_config_manager().get_config()

    def run_pipeline(self):
        """データ取得 → 特徴量作成 → 学習 → 評価 のパイプライン"""
        try:

            # step 1: 市場のトレーニングデータ取得/集計
            self.training_status = {"progress": 10, "status": "Fetching raw crypto data...", "result": None}
            raw_data = self.crypto_data.get_data()

            # step 2: 特徴量エンジニアリング
            self.training_status = {"progress": 20, "status": "Processing feature dataset...", "result": None}
            feature_data = self.feature_model.create_features(raw_data)
            X, y = self.feature_model.select_lagged_features(feature_data)
#            X, y = self.feature_model.create_features_NEW(raw_data)
            X, y = self.scaler.fit_transform(X, y)

#            # ラグ特徴量を簡単に作成
#            lag_transformer = LagFeatures(variables=["close"], lags=[1, 2, 3])
#            df_transformed = lag_transformer.fit_transform(df)
#            print(df_transformed.head())
#                        rolling_transformer = WindowFeatures(
#                            variables=["close"],
#                            window=[3],  # 3期間のローリング
#                            functions=["mean", "std"]  # 移動平均と標準偏差
#                        )


            # step 3: アンサンブル学習 + 自動チューニング（ハイパーパラメータ最適化 Optuna）
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=True)

            self.training_status = {"progress": 60, "status": "Training ensemble model...", "result": None}
            self.ensemble_model.train(X_train, y_train)

            # step 4: モデルの評価
            self.training_status = {"progress": 80, "status": "Evaluating model...", "result": None}
            y_pred = self.ensemble_model.predict(X_test)
            importance = self.ensemble_model.get_feature_importance(X_test)
            eval_results = self.evaluator.evaluate(y_test, y_pred)


#            X_test, y_pred = self.scaler.inverse_transform(X_test, y_pred)
#            _, y_test = self.scaler.inverse_transform(X_test, y_test)

            print("Evaluation results:")
            print(importance)
            for metric, value in eval_results.items():
                print(f"{metric}: {value:.4f}")

            self.training_status = {"progress": 100, "status": "Completed", "result": None}

        except Exception as e:
            print(f"Training failed: {e}")
            self.training_status = {"progress": 100, "status": "Failed", "result": str(e), }
            raise e

