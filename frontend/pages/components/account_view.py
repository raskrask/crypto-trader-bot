import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_account_summary(st, balance):
    # --- 現在レート取得 ---
    btc_balance = balance['balance']['total'].get('BTC', 0)
    jpy_balance = balance['balance']['total'].get('JPY', 0)
    rate = balance['ticker'].get('last', 0)  # 現在価格（1BTCあたりのJPY）

    btc_in_jpy = btc_balance * rate
    total_jpy = btc_in_jpy + jpy_balance

    # --- 割合計算 ---
    labels = [f'BTC ({btc_balance:,.04f})', 'JPY']
    values = [btc_in_jpy, jpy_balance]

    data = pd.DataFrame({
        "資産": ["BTC", "JPY"],
        "金額": [btc_in_jpy, jpy_balance],
        "比率（%）": [
            round(btc_in_jpy / total_jpy * 100, 2) if total_jpy > 0 else 0,
            round(jpy_balance / total_jpy * 100, 2) if total_jpy > 0 else 0
        ]
    })

    # --- 円グラフ作成 ---
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            textinfo='label+percent',
            insidetextorientation='radial',
            marker=dict(colors=['#f7931a', '#2b8cbe'])
        )
    )

    # --- レイアウト調整 ---
    fig.update_layout(
        title_text=f"BTC/JPY 総額: {total_jpy:,.0f} 円",
        showlegend=True,
        height=300, width=100
    )
    st.plotly_chart(fig, use_container_width=True)

