# shared.py
import streamlit as st

def show_menu(active_page: str):
    st.markdown("""
        <style>
            .sidebar-header {
                text-align: center;
                margin-bottom: 1.5rem;
            }
            .sidebar-header img {
                width: 100px;
                margin-bottom: 0.3rem;
            }
            .sidebar-title {
                font-size: 1.2rem;
                font-weight: bold;
                color: #000000;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(
        """
        <div class="sidebar-header">
            <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png">
            <div class="sidebar-title">🌟 제니앱 (<a href='https://jeni.kr' target='_blank'>Jeni.kr</a>)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
