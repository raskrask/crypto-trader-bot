import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trade crypt")

st.title("💰 Trade crypt")


#---------------------------
from config.settings import settings

url = f"{settings.API_BASE}/api/trade/test"
response = requests.get(url)
st.write(response.json())
