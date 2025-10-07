import numpy as np
import pandas as pd
from models.ml.random_forest_model import RandomForestModel
from models.ml.xgboost_model import XGBoostModel
from models.ml.lightgbm_model import LightGBMModel
from models.ml.lstm_model import LSTMModel
from models.hyperparameter_optimizer import HyperparameterOptimizer
from models.ml.lgbm_classifier_model import LgbmClassifierModel

class EnsembleModel:
    def __init__(self, stage="staging", sequence_length=3 ):
        """ 各モデルを初期化（S3 からロードできる場合はロード） """
        self.stage = stage
        self.models = {
            "lgbm_classifier": LgbmClassifierModel(),
#            "random_forest": RandomForestModel(),
#            "xgboost": XGBoostModel(),
#            "lightgbm": LightGBMModel(),
#            "lstm": LSTMModel(sequence_length=sequence_length),
        }


    def train(self, X_train, y_train, y_name=None):
        """各モデルを学習"""
        for name, model in self.models.items():
            print(f"Training {name} for {y_name}...")
#            optimizer = HyperparameterOptimizer(model, X_train, y_train)
#            best_params = optimizer.optimize(n_trials=5)
#            model.set_hyperparams(best_params)

            model.train(X_train, y_train)
            model.save_to_s3(self.stage, y_name)

    def load_model(self, y_name):
        for name, model in self.models.items():
            model.load_from_s3(self.stage, y_name)

    def predict(self, X_test):
        """各モデルの予測結果を統合（平均）"""
        predictions = []
        for name, model in self.models.items():
            print(f"Predicting with {name}...")
            predictions.append(model.predict(X_test))

        prediction_shapes = [p.shape for p in predictions]
        if len(set(prediction_shapes)) > 1:
            min_size = min(p.shape[0] for p in predictions)
            print(f"Warning: Mismatched prediction sizes {prediction_shapes}. Resizing to {min_size}.")
            predictions = [p[:min_size] for p in predictions]

        predictions = np.array(predictions)
        return np.mean(predictions, axis=0).tolist()

    def get_feature_importance(self, X_test):
        results_list = []
        for name, model in self.models.items():
            feature_importance_df = model.get_feature_importance(X_test)
            feature_importance_df = feature_importance_df.reset_index()
            feature_importance_df.columns = ["Feature", "Importance"]
            feature_importance_df["ModelName"] = name

            results_list.append(feature_importance_df)

        return pd.concat(results_list, ignore_index=True)


