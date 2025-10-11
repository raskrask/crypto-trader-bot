import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.api_client import fetch_predictions, promote_model

st.set_page_config(page_title="Evaluate train models", layout="wide")

st.title("📈 Evaluate train models")

# API から予測データを取得
#@st.cache_data
def get_prediction_data():
    return fetch_predictions()

prediction_data = get_prediction_data()

if prediction_data:

    def clean_signal(arr):
        arr = list(map(float, arr[5:]))
        return [float(x) if x else None for x in arr]

    df = pd.DataFrame({
        "Date": pd.to_datetime(prediction_data["dates"][5:]),
        "price": clean_signal(prediction_data["price"]),
        "actual_buy_signal": clean_signal(prediction_data["actual_buy_signal"]),
        "actual_sell_signal": clean_signal(prediction_data["actual_sell_signal"]),
        "new_buy_model": clean_signal(prediction_data["new_buy_model"]),
        "new_sell_model": clean_signal(prediction_data["new_sell_model"]),    
        "current_buy_model": clean_signal(prediction_data["current_buy_model"]),
        "current_sell_model": clean_signal(prediction_data["current_sell_model"])
    })
    # **📊 実際の価格 vs 予測**
    st.subheader("📊 実際の価格と予測結果の比較からモデルを評価")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=("実際の価格 vs 新モデル予測", "現モデル予測"))
    # 上段
    fig.add_trace(go.Scatter(x=df["Date"], y=df["price"], mode="lines", name="実際の価格"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df["Date"], y=df["actual_buy_signal"], mode="lines", name="実際の価格判定（買）", line=dict(color="green", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["new_buy_model"], mode="lines", name="新モデル予測（買）", 
                             line=dict(color="rgba(0, 0, 255, 0.7)"), fill="tozeroy", fillcolor="rgba(0, 0, 255, 0.2)"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["current_buy_model"], mode="lines", name="現モデル予測（買）", line=dict(color="gray")), row=2, col=1)

    fig.add_trace(go.Scatter(x=df["Date"], y=df["actual_sell_signal"], mode="lines", name="実際の価格判定（売）", line=dict(color="red", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["new_sell_model"], mode="lines", name="新モデル予測（売）", 
                             line=dict(color="rgba(255, 0, 0, 0.7)"), fill="tozeroy", fillcolor="rgba(255, 0, 0, 0.2)"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["current_sell_model"], mode="lines", name="現モデル予測（売）", line=dict(color="purple")), row=2, col=1)

    # レイアウト
    fig.update_layout(height=600, width=900, title_text="実際の価格と予測結果の比較")
    st.plotly_chart(fig, use_container_width=True)

    # **📋 詳細データ**
    st.subheader("📋 予測データの詳細")
    st.dataframe(df)

    st.subheader("🛠 モデルの採用")
    if st.button("✅ 新しいモデルを本番に採用する"):
        if promote_model():
            st.success("新しいモデルを本番環境に適用しました！")
        else:
            st.error("モデルの適用に失敗しました。")

else:
    st.warning("データがありません。")


