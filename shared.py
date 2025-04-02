# shared.py
import streamlit as st

def show_menu(active_page: str):
    st.markdown("""
        <style>
            .sidebar-header {
                text-align: left;
                margin-bottom: 1.5rem;
            }
            .sidebar-header img {
                width: 140px;
                margin-bottom: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(
        """
        <div class="sidebar-header">
            <a href="/" target="_self">
                <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png" alt="Jeniapp Logo">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
