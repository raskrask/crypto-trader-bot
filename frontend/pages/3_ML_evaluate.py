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

#st.warning("1---------------")
st.warning(prediction_data["dates"][5:][:30])
st.warning(prediction_data["actual"][5:][:30])
st.warning(prediction_data["new_model"][5:][:30])
st.warning(prediction_data["current_model"][5:][:30])


if prediction_data:

    actual = list(map(int,prediction_data["actual"][5:]))
    actual = [ int(x) if x != -1 else None for x in actual ]

    new_model = list(map(int,prediction_data["new_model"][5:]))
    new_model = [ x if x != -1 else None for x in new_model ]

    current_model = list(map(int,prediction_data["current_model"][5:]))
    current_model = [ round(x) if x != -1 else None for x in current_model ]

    price = prediction_data["price"][5:len(current_model)]

    df = pd.DataFrame({
        "Date": pd.to_datetime(prediction_data["dates"][5:]),
        "price": price,
        "actual": actual,
        "new_model": prediction_data["new_model"][5:],
        "current_model": current_model
    })
    # **📊 実際の価格 vs 予測**
    st.subheader("📊 実際の価格と予測結果の比較からモデルを評価")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=("実際の価格 vs 新モデル予測", "現モデル予測"))
    # 上段
    fig.add_trace(go.Scatter(x=df["Date"], y=df["price"], mode="lines", name="実際の価格"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df["Date"], y=df["actual"], mode="lines", name="実際の価格判定"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["new_model"], mode="lines", name="新モデル予測"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["current_model"], mode="lines", name="現モデル予測"), row=2, col=1)

    # レイアウト
    fig.update_layout(height=600, width=900, title_text="実際の価格と予測結果の比較")

#    st.plotly_chart(fig, use_container_width=True)
#    fig = px.line(df, x="日付", y=["実際の価格", "新モデル予測", "現モデル予測"],
#                labels={"value": "価格", "variable": "データ"},
#                title="実際の価格 vs 予測値")
#    st.plotly_chart(fig, use_container_width=True)


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


