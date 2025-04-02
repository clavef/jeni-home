# shared.py
import streamlit as st

def show_menu(active_page: str):
    st.markdown("""
        <style>
            .sidebar-title {
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div class='sidebar-title'>🌟 <a href='/?page=home' target='_self' style='text-decoration: none; color: inherit;'>제니앱 (Jeni.kr)</a></div>", unsafe_allow_html=True)

    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
