import streamlit as st
import requests
import json
from utils.api_client import save_config, load_config

config = load_config()

st.title("⚙️ Config")
st.write("機械学習の条件設定")
market_symbol = st.selectbox("未対応）マーケット Symbol", ["BTC/JPY", "VITE/USDT"], index=["BTC/JPY", "VITE/USDT"].index(config["market_symbol"] or 0))
training_period_months = st.slider("学習データの月数", 1, 24, config["training_period_months"])
intervals = [1, 3, 5, 15, 30, 60, 60*2, 60*4, 60*6, 60*8, 60*12, 60*24, 60*24*3, 60*24*7]
training_timeframe = st.select_slider("学習データの足数（分数）",  options=intervals, value=config["training_timeframe"])
ensemble_ratio = st.slider("未対応）アンサンブルの割合 (LSTM)", 0.0, 1.0, config["ensemble_ratio"])
epochs = st.number_input("未対応）学習回数 (エポック数)", min_value=1, value=config["epochs"])
test_ratio = st.slider("未対応）検証データの割合", 0.1, 0.5, config["test_ratio"])

st.write("特徴量の条件設定")
feature_lag_X_BB = st.slider("説明変数のSMAとBB計算するラグ数（予測する対象の足数）", 2, 50, config["feature_lag_X_BB"])
feature_lag_X_ATR = st.slider("説明変数のATRの計算するラグ数（予測する対象の足数）", 1, 50, config["feature_lag_X_ATR"])
target_lag_Y = st.slider("目的変数の移動するラグ数（予測する対象の足数）", 1, 50, config["target_lag_Y"])

config = {
    "market_symbol": market_symbol,
    "training_period_months": training_period_months,
    "training_timeframe": training_timeframe,
    "ensemble_ratio": ensemble_ratio,
    "epochs": epochs,
    "test_ratio": test_ratio,
    "feature_lag_X_BB": feature_lag_X_BB,
    "feature_lag_X_ATR": feature_lag_X_ATR,
    "target_lag_Y": target_lag_Y
}


st.sidebar.markdown("# Settings")
if st.button("設定を送信") or st.sidebar.button("［設定を送信］"):
    response = save_config(config)

    if response.status_code == 200:
        st.success("設定が保存されました！")
    else:
        st.error("エラーが発生しました。")
