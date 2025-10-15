import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.components.account_view import render_account_summary
from pages.components.trading_view import render_predict_summary, render_candle_with_predict
from pages.components.order_form import render_order_form
from utils.api_client import get_balance, get_signals, get_transactions

st.set_page_config(page_title="Trade crypt")

st.title("💰 Trade crypt")

#@st.cache_data
def get_balance_data():
    return get_balance()

@st.cache_data
def get_signals_data():
    return get_signals()

col1, col2 = st.columns(2)

balance = get_balance_data()
render_account_summary(col1, balance)
render_order_form(col2, balance)


df_signals = pd.DataFrame(get_signals_data())
transaction_data = get_transactions()

render_predict_summary(col1, df_signals)
render_candle_with_predict(st, df_signals, transaction_data)


#---------------------------
from config.settings import settings

if st.button("Test API"):
    url = f"{settings.API_BASE}/api/trade/test"
    response = requests.get(url)
    st.write(response.json())
