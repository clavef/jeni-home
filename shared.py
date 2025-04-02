# shared.py
import streamlit as st

def show_menu(active_page: str):
    st.sidebar.page_link("home.py", label="제니앱", icon="🌟")
    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
