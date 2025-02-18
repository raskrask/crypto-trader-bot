import streamlit as st
import requests
import time
from utils.api_client import train_model

st.set_page_config(page_title="ML Train")

st.title("📚 Machine Learning Training")

if "training_status" not in st.session_state:
    st.session_state.training_status = "Not started"

st.write(f"Training Status: {st.session_state.training_status}")
if st.button("Start Training"):
    st.session_state.training_status = "Training started"
    response = train_model("start", method="POST")
    st.write(response["message"])
    st.rerun()

status_placeholder = st.empty()

while True:
    if st.session_state.training_status == "Training started":
        response = train_model("status")
        status_placeholder.write(f"Status: {response['status']}, Progress: {response['progress']}%")
        
        if response["status"] == "Completed":
            result = train_model("result")
            status_placeholder.write(f"Result: {result['result']}")
            st.session_state.training_status = "Completed"
            exec(open("pages/2_ml_evaluate.py").read())
            break
        if response["status"] == "Failed":
            status_placeholder.write(f"Result: Failed")
            st.session_state.training_status = "Failed"
            st.rerun()
            break
    
    time.sleep(5)
