import pickle
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from config.settings import settings
from utils.s3_helper import get_s3_helper
from config import constants

class LogZScalerProcessor:
    def __init__(self, stage="staging"):
        self.scaler_X = StandardScaler()
        self.is_fitted = False
        self.stage = stage
        self.s3 = get_s3_helper()

    def fit_transform(self, X):
        X_transformed = self._log_transform(X)
        X_scaled = self.scaler_X.fit_transform(self._convert_to_numpy(X_transformed))

        self.is_fitted = True
        self.save()

        return self._convert_back(X, X_scaled)

    def transform(self, X):
        if not self.is_fitted:
            self.load()

        X_transformed = self._log_transform(X)
        X_scaled = self.scaler_X.transform(self._convert_to_numpy(X_transformed))

        return self._convert_back(X, X_scaled)

    def inverse_transform(self, X):
        if not self.is_fitted:
            self.load()

        X_original = self.scaler_X.inverse_transform(self._convert_to_numpy(X))
        X_reverted = self._inverse_log_transform(X_original)

        return self._convert_back(X, X_reverted)

    def get_s3_filename(self):
        return f"{constants.S3_FOLDER_MODEL}/{self.stage}/log_z_scaler.pkl"

    def save(self):
        self.s3.save_pkl_to_s3(self.scaler_X, self.get_s3_filename())

    def load(self):
        self.scaler_X = self.s3.load_pkl_from_s3(self.get_s3_filename())
        self.is_fitted = True

    def _log_transform(self, data):
        """ log(1 + x) 変換を適用（負の値の処理を考慮） """
        return np.log1p(np.maximum(self._convert_to_numpy(data), 0))

    def _inverse_log_transform(self, data):
        """ 逆変換：exp(x) - 1 """
        return np.expm1(data)

    def _convert_to_numpy(self, data):
        if isinstance(data, pd.DataFrame):
            return data.values
        elif isinstance(data, pd.Series):
            return data.values.reshape(-1, 1)
        elif isinstance(data, list):
            return np.array(data).reshape(-1, 1)
        return data

    def _convert_back(self, original_data, transformed_data):
        if isinstance(original_data, pd.DataFrame):
            return pd.DataFrame(transformed_data, columns=original_data.columns, index=original_data.index)
        elif isinstance(original_data, pd.Series):
            return pd.Series(transformed_data.flatten(), index=original_data.index, name=original_data.name)
        elif isinstance(original_data, list):
            return transformed_data.tolist()
        return transformed_data
