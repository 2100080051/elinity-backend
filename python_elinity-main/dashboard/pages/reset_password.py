import streamlit as st
from dashboard.config import get_api_url
import requests

def reset_password_page():
    st.title("Reset Password")
    email = st.text_input("Email")
    if st.button("Reset"):
        url = f"{get_api_url()}/auth/reset-password"
        response = requests.post(url, json={"email": email})
        if response.status_code == 200:
            st.success("Password reset email sent")
        else:
            st.error("Reset failed")
