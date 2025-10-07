import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from config.settings import settings

st.set_page_config(page_title="Debug Pages", layout="wide")

# ---------------------------
if st.button("ML Train debug"):
    url = f"{settings.API_BASE}/api/debug/"
    response = requests.get(url)
    st.write(response.json())
