import streamlit as st
from shared import show_menu

show_menu("home")

# 홈 타이틀 영역에 좌측 정렬된 로고 표시
st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <img src="https://raw.githubusercontent.com/clavef/jeniapp/main/logo.png" alt="Jeniapp Logo" style="height: 40px;">
    </div>
""", unsafe_allow_html=True)

# 소개 문구
st.markdown("생활과 업무를 편리하게 만들어주는 다양한 도구들을 제니앱에서 만나보세요.")

# 인스타 언팔체크 섹션
st.subheader("📱 인스타 언팔체크")
st.markdown("Instagram에서 다운로드한 JSON 데이터를 분석해, 내가 팔로우하지만 나를 팔로우하지 않는 계정을 찾아줍니다.")
st.page_link("pages/check.py", label="인스타 언팔체크 실행하기")

# 카드값 계산기 섹션
st.subheader("💳 카드값 계산기")
st.markdown("여러 카드사에서 받은 월별 이용내역을 업로드하면 하나의 통합표로 정리해줍니다.")
st.page_link("pages/cards.py", label="카드값 계산기 실행하기")
