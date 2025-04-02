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
            .sidebar-logo {
                display: block;
                margin: 0 auto 10px auto;
            }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 로고 이미지 삽입
    st.sidebar.markdown(
        """
        <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png" width="80" class="sidebar-logo">
        """,
        unsafe_allow_html=True
    )

    # 기존 타이틀 텍스트
    st.sidebar.markdown(
        "<div class='sidebar-title'>🌟 <a href='/?page=home' target='_self' style='text-decoration: none; color: inherit;'>제니앱 (Jeni.kr)</a></div>",
        unsafe_allow_html=True
    )

    # 메뉴 항목
    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
