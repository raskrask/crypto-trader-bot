import numpy as np
from models.ml.random_forest_model import RandomForestModel
from models.ml.xgboost_model import XGBoostModel
from models.ml.lightgbm_model import LightGBMModel
from models.ml.lstm_model import LSTMModel
from models.hyperparameter_optimizer import HyperparameterOptimizer

class EnsembleModel:
    def __init__(self, stage="staging", sequence_length=3 ):
        """ 各モデルを初期化（S3 からロードできる場合はロード） """
        self.stage = stage
        self.models = {
#            "random_forest": RandomForestModel(),
            "xgboost": XGBoostModel(),
#            "lightgbm": LightGBMModel(),
#            "lstm": LSTMModel(sequence_length=sequence_length),
        }


    def train(self, X_train, y_train):
        """各モデルを学習"""
        for name, model in self.models.items():
            print(f"Training {name}...")
#            optimizer = HyperparameterOptimizer(model, X_train, y_train)
#            best_params = optimizer.optimize(n_trials=5)
#            model.set_hyperparams(best_params)

            model.train(X_train, y_train)
            model.save_to_s3(self.stage)

    def train_OLD(self, X_train, y_train):
        """各モデルを学習"""
        for name, model in self.models.items():
            print(f"Training {name}...")
            optimizer = HyperparameterOptimizer(model, X_train, y_train)
            best_params = optimizer.optimize(n_trials=5)
            model.set_hyperparams(best_params)

            # シーケンスモデルなら形状を変換
            if model.is_sequence_model():
                X_train = X_train.values.reshape(X_train.shape[0], X_train.shape[1], 1)

            model.train(X_train, y_train)
            model.save_to_s3(self.stage)

    def load_model(self):
        for name, model in self.models.items():
            model.load_from_s3(self.stage)

    def save_model(self, stage=None):
        for name, model in self.models.items():
            model.load_from_s3(stage or self.stage)

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
        results = []
        for name, model in self.models.items():
            results.append(model.get_feature_importance(X_test))
        return results
