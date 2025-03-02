import yfinance as yf 
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta
from utils.s3_helper import get_s3_helper
from config import constants
from config.config_manager import get_config_manager

class EconomicData():
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.s3 = get_s3_helper()

    def get_economic_indicators(self, start_date):
        indicators = {
            'DXY': 'DX-Y.NYB',
            'US10Y': '^TNX',
            'VIX': '^VIX',
            'S&P500': '^GSPC',
            'Nasdaq': '^IXIC'
        }
        period = (pd.Timestamp(datetime.now().date()) - start_date).days
        df_list = []

        for key, ticker in indicators.items():
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{period}d")
            if not hist.empty:
                temp_df = hist[['Close']].rename(columns={'Close': key})
                df_list.append(temp_df)

        economic_df = pd.concat(df_list, axis=1)
        economic_df = economic_df.ffill().dropna()

        # タイムスタンプ整理
        economic_df = economic_df.reset_index().rename(columns={"Date": "timestamp"})
        economic_df["timestamp"] = pd.to_datetime(economic_df["timestamp"])
        economic_df["timestamp"] = economic_df["timestamp"].dt.tz_localize(None)
        economic_df["timestamp"] = economic_df["timestamp"].dt.floor("D")

        # 足の間隔を変更
        interval_min = self.config_data.get("training_timeframe") 
        if interval_min < 60:
            economic_df = economic_df.resample(f"{interval_min}T").ffill()
        elif interval_min < 60 * 24:
            economic_df = economic_df.resample(f"{interval_min/60}H").ffill()

        # 変動率の計算＋スケーリング
        returns_df = economic_df.set_index("timestamp").pct_change().dropna()
        scaler = StandardScaler()
        scaled_returns = scaler.fit_transform(returns_df)
        scaled_returns_df = pd.DataFrame(scaled_returns, columns=returns_df.columns, index=returns_df.index)
        economic_df = scaled_returns_df.reset_index()

        return economic_df
