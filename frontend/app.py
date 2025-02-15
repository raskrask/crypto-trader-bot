import streamlit as st

import pages.home as home
import pages.history as history

# サイドメニュー
st.sidebar.markdown("# Crypto Trader Bot")
menu = st.sidebar.radio("Menu", ["🏠 ホーム", "📈 データ", "📊 価格推移（VIT)", "⚙️ 設定"])

# 各ページを呼び出す
if menu == "🏠 ホーム２":
    home.show()
elif menu == "📊 価格推移（VIT)":
    history.show()

