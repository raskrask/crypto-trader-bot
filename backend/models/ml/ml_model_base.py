import os
from abc import ABC, abstractmethod
from config.settings import settings
from utils.s3_helper import get_s3_helper

class MLModelBase(ABC):
    def __init__(self, sequence_model: bool = False):
        self.model = None
        self.sequence_model = sequence_model
        self.s3 = get_s3_helper()

    @abstractmethod
    def train(self, X_train, y_train):
        pass

    @abstractmethod
    def predict(self, X_test):
        pass

    @abstractmethod
    def _save_model(self, path):
        pass

    @abstractmethod
    def _load_model(self, path):
        pass

    @abstractmethod
    def _get_model_filename(self):
        pass

    def is_sequence_model(self):
        return self.sequence_model 

    def save_to_s3(self, stage):
        """
        s3_folder/ml_models/staging/lstm_model.keras
        """
        filename = self._get_model_filename()
        tmp_key = f"tmp/{filename}"
        s3_key = f"{settings.S3_FOLDER_MODEL}/{stage}/{filename}"
        self._save_model(tmp_key)
        self.s3.upload_to_s3(tmp_key, s3_key, delete_local=True)

    def load_from_s3(self, stage):
        filename = self._get_model_filename()
        tmp_key = f"tmp/{filename}"
        s3_key = f"{settings.S3_FOLDER_MODEL}/{stage}/{filename}"
        if self.s3.download_file( s3_key, tmp_key ):
            self._load_model(tmp_key)
            os.remove(tmp_key) 

