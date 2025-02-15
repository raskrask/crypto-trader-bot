# utils/data_processing.py
import numpy as np
import pandas as pd

import numpy as np
import pandas as pd

def generate_sequences(data, sequence_length, target_column=0):
    """
    時系列データを LSTM 用に変換。
    - `data`: DataFrame または NumPy 配列（形状: `(samples, features)`）
    - `sequence_length`: シーケンスの長さ（過去何ステップを1つの入力とするか）
    - `target_column`: 目的変数のカラムインデックス（デフォルト: 0）
    """
    sequences = []
    targets = []

    if isinstance(data, pd.DataFrame):
        data_array = data.to_numpy()
    else:
        data_array = data

    if len(data_array) < sequence_length:
        return np.empty((0, sequence_length, data_array.shape[1])), np.empty((0,))

    for i in range(len(data_array) - sequence_length):
        sequences.append(data_array[i:i + sequence_length, :])
        targets.append(data_array[i + sequence_length, target_column])

    return np.array(sequences), np.array(targets)


def convert_to_lag_features(df, target_column, lag_steps):
    """
    指定した列をラグ変換して特徴量を作成。
    - `df`: pandas DataFrame
    - `target_column`: ラグを作成する対象のカラム名
    - `lag_steps`: ラグを作成する数（例: 10なら過去10日分のデータを追加）
    """
    df_lagged = df.copy()
    for i in range(1, lag_steps + 1):
        df_lagged[f"{target_column}_lag_{i}"] = df[target_column].shift(i)
    
    df_lagged.dropna(inplace=True)  # 欠損値を削除
    return df_lagged

