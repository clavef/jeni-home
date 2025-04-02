# home.py
import streamlit as st
st.set_page_config(page_title="제니앱", page_icon="🌟", layout="wide")

from shared import show_menu

show_menu("home")

# 홈 타이틀 영역에 좌측 정렬된 로고 표시 (1.5배 확대)
st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
        <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png" alt="Jeniapp Logo" style="height: 60px;">
    </div>
""", unsafe_allow_html=True)

# 소개 문구
st.markdown("생활과 업무를 편리하게 만들어주는 다양한 도구들을 제니앱에서 만나보세요.")
st.markdown("\n---")

# 인스타 언팔체크 섹션
st.subheader("📱 인스타 언팔체크")
st.markdown("Instagram에서 다운로드한 JSON 데이터를 분석해, 내가 팔로우하지만 나를 팔로우하지 않는 계정을 찾아줍니다.")
st.page_link("pages/check.py", label="인스타 언팔체크 실행하기")

# 카드값 계산기 섹션
st.subheader("💳 카드값 계산기")
st.markdown("여러 카드사에서 받은 월별 이용내역을 업로드하면 하나의 통합표로 정리해줍니다.")
st.page_link("pages/cards.py", label="카드값 계산기 실행하기")

# 정산 도우미 섹션
st.subheader("📊 정산 도우미")
st.markdown("CSV 기반의 엑셀 정산 파일을 업로드하면 항목을 자동 분석하고, 데이터 병합과 분류 작업을 도와줍니다.")
st.page_link("pages/audit.py", label="정산 도우미 실행하기")

st.markdown("\n---")
st.markdown("ℹ️ 향후 다양한 도구들이 이곳에 추가될 예정입니다.")
st.caption("© 2025 제니앱 · 문의: id@matt.kr")
