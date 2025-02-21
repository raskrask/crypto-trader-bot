import streamlit as st
import requests
import pandas as pd
import plotly.express as px
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
    new_model = [ int(x) if x != -1 else None for x in new_model ]

    current_model = list(map(int,prediction_data["current_model"][5:]))
    current_model = [ int(x) if x != -1 else None for x in current_model ]


    df = pd.DataFrame({
        "日付": pd.to_datetime(prediction_data["dates"][5:]),
        "実際の価格": actual,
        "新モデル予測": list(map(int,prediction_data["new_model"][5:])),
        "現モデル予測": current_model
    })
    # **📊 実際の価格 vs 予測**
    st.subheader("📊 実際の価格と予測結果の比較からモデルを評価")
    fig = px.line(df, x="日付", y=["実際の価格", "新モデル予測", "現モデル予測"],
                labels={"value": "価格", "variable": "データ"},
                title="実際の価格 vs 予測値")
    fig.update_layout(yaxis=dict(range=[80000, 120000]))
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


