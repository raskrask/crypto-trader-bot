from lightgbm import LGBMClassifier
import pickle
from .ml_model_base import MLModelBase

class LgbmClassifierModel(MLModelBase):
    def __init__(self, **params):
        super().__init__()
        self.model_type = "lgbm_classifier"
        self.model = LGBMClassifier(**params)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        #return self.model.predict(X_test)
        return self.model.predict_proba(X_test)[:,1]

    def get_feature_importance(self, X_train):
        return self._get_shap_feature_importance(X_train)

    def suggest_hyperparams(self, trial):
        return {
#            "n_estimators": trial.suggest_int("n_estimators", 50, 500),
#            "max_depth": trial.suggest_int("max_depth", 3, 20),
#            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
#            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
        }

    def set_hyperparams(self, params):
        """最適化されたハイパーパラメータを適用"""
        self.model.set_params(**params)

    def _export_model(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def _import_model(self, path):
        with open(path, "rb") as f:
            self.model = pickle.load(f)

    def _get_model_filename(self):
        return f"{self.model_type}_model.txt"

