# shared.py
import streamlit as st

def show_menu(active_page: str):
    st.markdown("""
        <style>
            .sidebar-header {
                text-align: left;
                margin-bottom: 0.8rem; /* 기존 1.5rem → 줄임 */
            }
            .sidebar-header img {
                width: 140px;
                margin-bottom: 0.3rem; /* 기존 0.5rem → 줄임 */
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

    # 표시되는 페이지들
    st.sidebar.page_link("pages/check.py", label="인스타 언팔체크", icon="📱")
    st.sidebar.page_link("pages/cards.py", label="카드값 계산기", icon="💳")

    # 숨긴 페이지 → 버튼으로 이동 처리
    if st.sidebar.button("📊 정산 도우미"):
        st.switch_page("pages/_audit.py")
