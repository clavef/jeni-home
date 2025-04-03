# shared.py (v7)
import streamlit as st

def show_menu(active_page: str):
    st.markdown("""
        <style>
            .sidebar-header {
                text-align: left;
                margin-bottom: 0.8rem;
            }
            .sidebar-header img {
                width: 140px;
                margin-bottom: 0.3rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # 홈 링크를 실제로 동작하는 page_link로 처리
    st.sidebar.page_link("home.py", label="", icon=None)

    # 그 아래에 로고 이미지를 덮어 씌우듯 표시
    st.sidebar.markdown(
        """
        <div class="sidebar-header" style="margin-top: -2.5rem;">
            <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png" alt="Jeniapp Logo">
        </div>
        """,
        unsafe_allow_html=True
    )

    # 메뉴 링크들
    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
