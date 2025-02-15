from lightgbm import LGBMRegressor, Booster
from .ml_model_base import MLModelBase

class LightGBMModel(MLModelBase):
    def __init__(self, **params):
        super().__init__()
        self.model_type = "lightgbm"
        self.model = LGBMRegressor(**params)
        self.is_booster_loaded = False

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        self.is_booster_loaded = False

    def predict(self, X_test):
        if self.is_booster_loaded and hasattr(self.model, "_Booster"):
            return self.model._Booster.predict(X_test)
        return self.model.predict(X_test)

    def suggest_hyperparams(self, trial):
        """Optuna でのハイパーパラメータ設定"""
        return {
            "n_estimators": trial.suggest_int("n_estimators", 50, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "num_leaves": trial.suggest_int("num_leaves", 20, 60),
            "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0.0001, 0.01),
            "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 5, 50),
        }

    def set_hyperparams(self, params):
        """最適化されたハイパーパラメータを適用"""
        self.model.set_params(**params)

    def _save_model(self, path):
        self.model.booster_.save_model(path)

    def _load_model(self, path):
        self.model = LGBMRegressor()
        self.model._Booster = Booster(model_file=path)
        self.is_booster_loaded = True

    def _get_model_filename(self):
        return f"{self.model_type}_model.txt"

