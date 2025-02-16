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


