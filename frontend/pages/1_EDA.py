import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from config.settings import settings

st.set_page_config(page_title="Explanatory Data Analysis", layout="wide")

st.title("🔍 Explanatory Data Analysis")

#---------------------------
if st.button("仮説：アルトコインとBTCの相関関係"):

    st.markdown("""
        ### 仮説
        アルトコインを売買対象通貨としたときに、BTCが仮想通貨市場全体に大きな影響を与えるため、BTCとの強い相関関係があると考えられる。
        | BTC時価総額 | BTCドミナンス | 市場の傾向 |
        | ---- | ---- | ---- |
        | 上昇 | 上昇 | BTCに資金が集中（安全資産として買われる）|
        | 上昇 | 下降 | BTCとともにアルトコインも上昇（アルトシーズン）|
        | 下降 | 上昇 | 投資家がアルトコインからBTCへ資金移動（アルト売り）|
        | 下降 | 下降 | 仮想通貨市場全体が下落（リスク回避でUSDTや法定通貨へ逃避）|
        """)

    url = f"{settings.API_BASE}/api/eda/explore"
    response = requests.get(url)
    st.write(response.json())

    df_vite = pd.DataFrame(response.json()['VITE/USDT'])
    df_btc = pd.DataFrame(response.json()['BTC/USDT'])

    # 2列のカラムを作成
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### VITE/USDT の 1日足データ")
        st.dataframe(df_vite)

    with col2:
        st.write(f"### Close価格の推移をグラフ化")
        #st.line_chart(df_vite.set_index("timestamp")["close"])
        #st.line_chart(df_btc.set_index("timestamp")["close"]) 


        df = pd.DataFrame({
            "日付": pd.to_datetime(df_vite["timestamp"]),
            "VITE/USDT": df_vite["close"],
            "BTC/USDT": df_btc["close"]
        })

        st.subheader("📊 VITE, BTCの指定日の比較")
        fig = px.line(df, x="日付", y=["VITE/USDT", "BTC/USDT"],
                        labels={"value": "価格", "variable": "データ"})
        fig.update_layout(yaxis=dict(range=[80000, 120000]))
        st.plotly_chart(fig, use_container_width=True)



    col3, col4 = st.columns(2)
    with col3:
        # ローソク足チャート
        fig = go.Figure(data=[
            go.Candlestick(
                x=df_vite["timestamp"],
                open=df_vite["open"],
                high=df_vite["high"],
                low=df_vite["low"],
                close=df_vite["close"],
            )
        ])
        fig.update_layout(title=f"VITE/USDT ローソク足チャート", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig)  # Streamlitで表示

    with col4:
        # ボックスプロット
        fig = px.box(df_vite, y="close", title=f"VITE/USDT の価格分布")
        st.plotly_chart(fig)