from xgboost import XGBRegressor
import optuna
from .ml_model_base import MLModelBase

class XGBoostModel(MLModelBase):
    def __init__(self, **params):
        super().__init__()
        self.model_type = "xgboost"
        self.model = XGBRegressor(**params)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)

    def _save_model(self, path):
        self.model.save_model(path)

    def _load_model(self, path):
        self.model.load_model(path)

    def _get_model_filename(self):
        return f"{self.model_type}_model.json"

    def suggest_hyperparams(self, trial):
        """Optuna でのハイパーパラメータ設定"""
        return {
            "n_estimators": trial.suggest_int("n_estimators", 50, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        }

    def set_hyperparams(self, params):
        """最適化されたハイパーパラメータを適用"""
        self.model.set_params(**params)
