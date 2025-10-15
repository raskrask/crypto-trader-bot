import streamlit as st
from utils.api_client import post_limit_order

def render_order_form(container, balance):

    btc_balance = balance['balance']['total'].get('BTC', 0)
    jpy_balance = balance['balance']['total'].get('JPY', 0)
    rate = balance['ticker'].get('last', 0)  # 現在価格（1BTCあたりのJPY）

    btc_in_jpy = btc_balance * rate
    total_jpy = btc_in_jpy + jpy_balance

    if "order_price" not in st.session_state:
        st.session_state.order_price = str(rate)
    if "order_amount" not in st.session_state:
        st.session_state.order_amount = str(btc_balance)

    # --- 注文入力 ---
    col1, col2 = container.columns(2)
    with col1:
        order_price = col1.text_input("注文価格", placeholder="BTC/JPY", key="order_price")
    with col2:
        order_amount = col2.text_input("注文量", placeholder="BTC", key="order_amount")

    # --- 概算（自動計算風） ---
    if order_price and order_amount:
        try:
            order_summary = float(order_price) * float(order_amount)
            container.text_input("概算", f"{order_summary:,.0f} 円", disabled=True)
        except ValueError:
            container.text_input("概算", "数値を入力してください", disabled=True)
    else:
        container.text_input("概算", "", disabled=True)

    side = container.radio(
        "注文種別",
        ["売り", "買い"],
        horizontal=True,
    )

    # --- 注文ボタン ---
    if container.button("✅ 注文する", use_container_width=True):
        if not side:
            container.warning(f"「売り」か「買い」を選択してください。")
        elif not order_price or not order_amount:
            container.error("価格と数量を入力してください。")
        elif float(order_amount) < 0.001:
            container.error("最低取り扱い数に達していません。")
        elif side == "買い" and (float(order_price) * float(order_amount)) > jpy_balance:
            container.error("購入価格が大きすぎます")
        elif side == "売り" and float(order_amount) > btc_balance:
            container.error("注文売却数が不足しています")
        elif (float(order_price) * float(order_amount)) > 1_000_000:
            container.error("取り扱い金額が大きすぎます")
        elif (float(order_price) / rate) > 1.2 or (float(order_price) / rate) < 0.8:
            container.error("注文価格と現在価格の差が大きすぎます")
        else:
            side_map = {"買い": "buy", "売り": "sell"}
            response = post_limit_order(side_map[side], order_amount, order_price)
            if response.ok:
                container.success(f"{side}注文を送信しました。")
            else:
                st.error(f"エラーが発生しました。{response.text}")
