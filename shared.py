# shared.py
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

    # 페이지 제목을 기준으로 switch_page 해야 함
    if st.sidebar.button("📱 인스타 언팔체크"):
        st.switch_page("인스타 언팔체크")

    if st.sidebar.button("💳 카드값 계산기"):
        st.switch_page("카드값 계산기")

    if st.sidebar.button("📊 정산 도우미"):
        st.switch_page("정산 도우미")
