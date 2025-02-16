from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

class Evaluator:
    def __init__(self):
        pass

    def evaluate(self, y_true, y_pred):
        """モデルの評価指標を計算"""

#        if len(y_true) > len(y_pred):
#            y_true = y_true[:len(y_pred)]

        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        results = {
            "MSE": mse,
            "RMSE": rmse,
            "MAE": mae,
            "R2 Score": r2
        }

        return results

        