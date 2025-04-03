# shared.py (v8)
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

    # 로고는 장식용 고정
    st.sidebar.markdown(
        """
        <div class="sidebar-header">
            <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png" alt="Jeniapp Logo">
        </div>
        """,
        unsafe_allow_html=True
    )

    # 명시적 홈 메뉴 추가
    st.sidebar.page_link("home.py", label="제니앱 홈 [Jeni.kr]", icon="🏠")
    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")
    st.sidebar.page_link("pages/audit.py", label="정산 도우미", icon="📊")
