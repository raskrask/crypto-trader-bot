import pickle
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from config.settings import settings
from utils.s3_helper import get_s3_helper

class MinMaxScalerProcessor:
    def __init__(self, stage="staging", feature_range=(0, 1)):
        self.scaler_X = MinMaxScaler(feature_range=feature_range)
        self.scaler_y = MinMaxScaler(feature_range=feature_range)
        self.is_fitted = False
        self.stage = stage
        self.s3 = get_s3_helper()

    def fit_transform(self, X, y):
        X_scaled = self.scaler_X.fit_transform(self._convert_to_numpy(X))
        y_scaled = self.scaler_y.fit_transform(self._convert_to_numpy(y))

        self.is_fitted = True
        self.save()
        return self._convert_back(X, X_scaled), self._convert_back(y, y_scaled)

    def transform(self, X, y=None):
        if not self.is_fitted:
            self.load()

        X_scaled = self.scaler_X.transform(self._convert_to_numpy(X))
        if y is None:
            return self._convert_back(X, X_scaled), None

        y_scaled = self.scaler_y.transform(self._convert_to_numpy(y))
        return self._convert_back(X, X_scaled), self._convert_back(y, y_scaled)

    def inverse_transform(self, X, y=None):
        if not self.is_fitted:
            self.load()

        X_original = self.scaler_X.inverse_transform(self._convert_to_numpy(X))
        if y is None:
            return self._convert_back(X, X_original), None

        y_original = self.scaler_y.inverse_transform(self._convert_to_numpy(y))
        return self._convert_back(X, X_original), self._convert_back(y, y_original)

    def get_s3_filename(self, type):
        """
        s3_folder/ml_models/staging/X_min_max_scaler_Xy.pkl
        """
        return f"{settings.S3_FOLDER_MODEL}/{self.stage}/min_max_scaler_{type}.pkl"

    def save(self):
        self.s3.save_pkl_to_s3(self.scaler_X, self.get_s3_filename('X'))
        self.s3.save_pkl_to_s3(self.scaler_y, self.get_s3_filename('y'))

    def load(self):
        self.scaler_X = self.s3.load_pkl_from_s3(self.get_s3_filename('X'))
        self.scaler_y = self.s3.load_pkl_from_s3(self.get_s3_filename('y'))
        self.is_fitted = True

    def _convert_to_numpy(self, data):
        if isinstance(data, pd.DataFrame):
            return data.values  # DataFrame → NumPy 配列
        elif isinstance(data, pd.Series):
            return data.values.reshape(-1, 1)  # Series → (n,1) に変換
        elif isinstance(data, list):
            return np.array(data).reshape(-1, 1)  # list → (n,1) に変換
        return data

    def _convert_back(self, original_data, transformed_data):
        if isinstance(original_data, pd.DataFrame):
            return pd.DataFrame(transformed_data, columns=original_data.columns, index=original_data.index)
        elif isinstance(original_data, pd.Series):
            return pd.Series(transformed_data.flatten(), index=original_data.index, name=original_data.name)
        elif isinstance(original_data, list):
            return transformed_data.tolist()
        return transformed_data
