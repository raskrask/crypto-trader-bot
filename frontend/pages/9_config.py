import streamlit as st
import requests
import json
from utils.api_client import save_config, load_initial_config

config = load_initial_config()

st.title("⚙️ Config")
st.write("機械学習の条件設定")
market_symbol = st.selectbox("マーケット Symbol", ["BTC/JPY", "VITE/USDT"], index=["BTC/JPY", "VITE/USDT"].index(config["market_symbol"]))
training_period_months = st.slider("学習データの月数", 1, 24, config["training_period_months"])
ensemble_ratio = st.slider("アンサンブルの割合 (LSTM)", 0.0, 1.0, config["ensemble_ratio"])
epochs = st.number_input("学習回数 (エポック数)", min_value=1, value=config["epochs"])
test_ratio = st.slider("検証データの割合", 0.1, 0.5, config["test_ratio"])

config = {
    "market_symbol": market_symbol,
    "training_period_months": training_period_months,
    "ensemble_ratio": ensemble_ratio,
    "epochs": epochs,
    "test_ratio": test_ratio
}

if st.button("設定を送信"):
    response = save_config(config)

    if response.status_code == 200:
        st.success("設定が保存されました！")
    else:
        st.error("エラーが発生しました。")
