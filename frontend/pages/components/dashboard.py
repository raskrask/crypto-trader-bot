import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.api_client import get_trade_history

def show(st):
    st.set_page_config(page_title="Dashboard", layout="wide")

    st.title("Machine Learning Trade")
    #購入価格と現在価格の推移 - 購入時点と現在の価格を比較
    #含み損益の推移 - 各取引ごとの未決済の損益を可視化
    #実現損益の推移 - 売却済みの累積利益を表示
    #投資額 vs 評価額の推移 - 投資額と現在評価額を比較

    history = get_trade_history()
    df = pd.DataFrame({
        "Date": history["dates"],
        "Predicted Price": history["predicted_price"],
        "Purchase Price": history["purchase_prices"],
        "Current Price": history["current_prices"],
        "Investment Amount (BTC)": history["investment_amounts"],
        "Unrealized Gains (JPY)": history["unrealized_gains"],
        "Realized Profits (JPY)": history["realized_profits"]
    })
    #st.write(history)

    # 2列のカラムを作成
    col1, col2 = st.columns(2)
    with col1:
        # ① 予想価格と現在価格の推移
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Predicted Price"], mode="lines+markers", name="予想価格"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Current Price"], mode="lines+markers", name="現在価格", line=dict(dash="dash")))
        fig.update_layout(
            title="WIP ① 予想価格と現在価格の推移", legend=dict(title="", x=0, y=0),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ③ 実現損益の推移
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Realized Profits (JPY)"], mode="lines+markers", name="累積損益", line=dict(color="blue")))
        fig.update_layout( title="WIP ③ 実現損益の推移" )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # ② 含み損益の推移
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Date"], y=df["Unrealized Gains (JPY)"], name="含み損益", marker=dict(color=["green" if x > 0 else "red" for x in df["Unrealized Gains (JPY)"]])))
        fig.update_layout( title="WIP ② 含み損益の推移" )
        st.plotly_chart(fig, use_container_width=True)

        # ④ 投資額 vs 評価額の推移
        fig = go.Figure()
        investment_values = df["Investment Amount (BTC)"] * df["Purchase Price"]
        evaluation_values = df["Investment Amount (BTC)"] * df["Current Price"]
        fig.add_trace(go.Bar(x=df["Date"], y=investment_values, name="投資額", opacity=0.6))
        fig.add_trace(go.Bar(x=df["Date"], y=evaluation_values, name="評価額", opacity=0.6))
        fig.update_layout(
            title="WIP ④ 投資額 vs 評価額の推移", legend=dict(x=0, y=0),
        )
        st.plotly_chart(fig, use_container_width=True)

