import streamlit as st
from dashboard.config import get_api_url
import requests

def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        url = f"{get_api_url()}/auth/token"
        response = requests.post(url, data={"username": email, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token
            st.success("Logged in")
        else:
            st.error("Login failed")
