import optuna
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class HyperparameterOptimizer:
    def __init__(self, ml_model, X_trial, y_trial):
        self.ml_model = ml_model
        self.X_trial = X_trial
        self.y_trial = y_trial
        self.best_params = None

    def objective(self, trial):
        """Optuna で最適化する目的関数"""

        # モデルに最適なハイパーパラメータを適用
        params = self.ml_model.suggest_hyperparams(trial)
        self.ml_model.set_hyperparams(params)

        # LSTM の場合、データの形状を変換
        if self.ml_model.is_sequence_model():
            X_train_lstm = self.X_trial.values.reshape(self.X_trial.shape[0], self.X_trial.shape[1], 1)
            self.ml_model.train(X_train_lstm, self.y_trial)
            return self.ml_model.evaluate(self.X_trial, self.y_trial)["loss"]

        # それ以外は通常のデータ分割
        X_train, X_test, y_train, y_test = train_test_split(self.X_trial, self.y_trial, test_size=0.2, random_state=42)
        self.ml_model.train(X_train, y_train)
        y_pred = self.ml_model.predict(X_test)

        return mean_squared_error(y_test, y_pred)  # MSE を最小化

    def optimize(self, n_trials=50):
        """Optuna で最適化を実行"""
        study = optuna.create_study(direction="minimize")
        study.optimize(self.objective, n_trials=n_trials)

        self.best_params = study.best_params
        print(f"Best parameters for {self.ml_model.model_type}: {self.best_params}")

        return self.best_params
