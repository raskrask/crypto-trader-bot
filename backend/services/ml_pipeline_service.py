import pandas as pd
import numpy as np
from models.crypto_training_dataset import CryptoTrainingDataset
from models.feature_dataset_model import FeatureDatasetModel
from models.scalers.log_z_scaler_processor import LogZScalerProcessor
from models.ensemble_model import EnsembleModel
from models.evaluator import Evaluator
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from config.config_manager import get_config_manager

class MlPipelineService:

    def __init__(self):
        self.training_status = {"progress": 0, "status": "Not started", "result": None}
        self.config_data = get_config_manager().get_config()

    def run_pipeline(self):
        """データ取得 → 特徴量作成 → 学習 → 評価 のパイプライン"""
        try:
            self.crypto_data = CryptoTrainingDataset()
            self.feature_model = FeatureDatasetModel()
            self.evaluator = Evaluator()
            self.scaler = LogZScalerProcessor()
            result = []

            # step 1: 市場のトレーニングデータ取得/集計
            self.training_status = {"progress": 10, "status": "Fetching raw crypto data...", "result": None}
            raw_data = self.crypto_data.get_data()

            # step 2: 特徴量エンジニアリング
            self.training_status = {"progress": 20, "status": "Processing feature dataset...", "result": None}
#            feature_data = self.feature_model.create_features(raw_data)
#            X, y = self.feature_model.select_lagged_features(feature_data)
            X, Y_vals = self.feature_model.create_features(raw_data)
            X = self.scaler.fit_transform(X)
            num_targets = len(Y_vals.columns)
            
            for i, y_name in enumerate(Y_vals.columns):
                y = Y_vals[[y_name]]#.rename(columns={y_name: 'target'})

                # step 3: アンサンブル学習 + 自動チューニング（ハイパーパラメータ最適化 Optuna）
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=True)

                y_train = y_train.values.ravel()
                y_test  = y_test.values.ravel()
                self.training_status = {"progress": 20+20//num_targets*(i*4+2), "status": f"Training ensemble model for {y_name}...", "result": None}
                self.ensemble_model = EnsembleModel()
                self.ensemble_model.train(X_train, y_train, y_name)

                # step 4: モデルの評価
                self.training_status = {"progress": 20+20//num_targets*(i*4+3), "status": f"Evaluating model for {y_name}...", "result": None}
                y_pred = self.ensemble_model.predict(X_test)
                y_pred_soft = (np.array(y_pred) > 0.5).astype(int)
                importance = self.ensemble_model.get_feature_importance(X_test)
                eval_results = self.evaluator.evaluate(y_test, y_pred)
                score = accuracy_score(y_test, pd.DataFrame(y_pred, columns=["buy_signal"], index=X_test.index).round())
                result = {"Accuracy": score, "importance": importance, "eval_results": eval_results}

                print("Accuracy:", accuracy_score(y_test, y_pred_soft))
                print("AUC:", roc_auc_score(y_test, y_pred))
                print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_soft))
    #            X_test, y_pred = self.scaler.inverse_transform(X_test, y_pred)

    #            print("Evaluation results:")
    #            print(importance)
    #            for metric, value in eval_results.items():
    #                print(f"{metric}: {value:.4f}")

            self.training_status = {"progress": 100, "status": f"Completed", "result": result}

        except Exception as e:
            print(f"Training failed: {e}")
            self.training_status = {"progress": 100, "status": "Failed", "result": str(e), }
            raise e

