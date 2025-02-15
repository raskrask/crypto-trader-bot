import os
import json
import logging
import boto3
import pandas as pd
import pickle
from typing import Any
from io import BytesIO
from botocore.exceptions import ClientError
from config.settings import settings
from functools import lru_cache

class S3Helper:
    def __init__(self):
        """S3 クライアントの初期化（シングルトン）"""
        session = boto3.Session(region_name=settings.AWS_REGION)
        self.s3 = session.client("s3")
        self.bucket_name = settings.S3_BUCKET

    def upload_to_s3(self, file_path: str, s3_key: str, delete_local: bool = True):
        """ローカルファイルを S3 にアップロード"""
        try:
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            if delete_local:
                os.remove(file_path)
        except ClientError as e:
            logging.error(f"S3へのアップロードエラー: {e}")
            raise

    def save_to_s3(self, buffer: BytesIO, s3_path: str):
        """バイナリデータを S3 に保存"""
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_path,
                Body=buffer.getvalue(),
                ContentType="application/octet-stream"
            )
        except ClientError as e:
            logging.error(f"S3への保存エラー: {e}")
            raise

    def save_json_to_s3(self, json_data: dict, file_key: str):
        """JSON データを S3 に保存"""
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=json.dumps(json_data),
                ContentType="application/json"
            )
        except ClientError as e:
            logging.error(f"S3へのJSON保存エラー: {e}")
            raise

    def load_json_from_s3(self, file_key: str):
        """S3 から JSON データを読み込み"""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            return json.loads(response['Body'].read().decode("utf-8"))
        except self.s3.exceptions.NoSuchKey:
            logging.warning(f"S3に {file_key} が見つかりません")
            return None
        except ClientError as e:
            logging.error(f"S3からJSON取得エラー: {e}")
            raise

    def save_parquet_to_s3(self, df: pd.DataFrame, file_key: str):
        """DataFrame を Parquet に変換し、S3 に保存"""
        try:
            buffer = BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)
            self.save_to_s3(buffer, file_key)
        except Exception as e:
            logging.error(f"S3へのParquet保存エラー: {e}")
            raise

    def load_parquet_from_s3(self, s3_key: str) -> pd.DataFrame:
        """S3 から Parquet ファイルをロード"""
        try:
            obj = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            return pd.read_parquet(BytesIO(obj["Body"].read()))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logging.warning(f"S3に {s3_key} が見つかりません")
                return pd.DataFrame()
            logging.error(f"S3からParquet取得エラー: {e}")
            raise

    def save_pkl_to_s3(self, obj, file_key: str):
        try:
            serialized = pickle.dumps(obj)
            self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=serialized)
        except Exception as e:
            logging.error(f"S3へのpickle保存エラー: {e}")
            raise

    def load_pkl_from_s3(self, s3_key: str) -> Any:
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            serialized = response['Body'].read()
            return pickle.loads(serialized)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logging.warning(f"S3に {s3_key} が見つかりません")
                return pd.DataFrame()
            logging.error(f"S3からpickle取得エラー: {e}")
            raise

    def download_file(self, s3_key: str, file_key: str) -> bool:
        try:
            self.s3.download_file(self.bucket_name, s3_key, file_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logging.warning(f"S3に {s3_key} が見つかりません")
                return False
            raise

# シングルトン化
@lru_cache
def get_s3_helper() -> S3Helper:
    """S3Helper のシングルトンインスタンスを取得"""
    return S3Helper()
