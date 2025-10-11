from lightgbm import LGBMClassifier
import pickle
from .ml_model_base import MLModelBase

class LgbmClassifierModel(MLModelBase):
    def __init__(self, **params):
        super().__init__()
        self.model_type = "lgbm_classifier"
        params = {
            "objective": "binary",
            "metric": "binary_logloss",    "learning_rate": 0.05,
            "num_leaves": 7,
            "max_depth": 3,
            "min_child_samples": 1,
            "min_split_gain": 0.0,
            "reg_alpha": 0.0,
            "reg_lambda": 0.0,
            "n_estimators": 200,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "verbosity": -1,
        }

        self.model = LGBMClassifier(**params)

    def train(self, X_train, y_train):
        try:
            import lightgbm as lgb

            self.model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train)],
                eval_metric="binary_logloss",
                callbacks=[lgb.log_evaluation(period=1)]  # ← 1イテごとに出力
            )
            print("✅ Training complete")
        except Exception as e:
            print("❌ Training failed:", e)

        import pandas as pd
        try:
            fi = pd.Series(self.model.feature_importances_, index=X_train.columns)
            print("Feature importances (non-zero):")
            print(fi[fi > 0].sort_values(ascending=False).head(10))
        except Exception as e:
            print("⚠️ No feature importances:", e)

        #self.model.fit(X_train, y_train)

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

