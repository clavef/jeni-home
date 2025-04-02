# home.py
import streamlit as st
st.set_page_config(page_title="제니앱", page_icon="🌟", layout="wide")

from shared import show_menu

show_menu("홈")

st.title("🌟 제니앱 (Jeni.kr)")
st.markdown("**생활과 업무를 편리하게 만들어주는 다양한 도구들을 제니앱에서 만나보세요.**")
st.markdown("---")

st.markdown("### 📱 인스타 언팔체크")
st.write("Instagram에서 다운로드한 JSON 데이터를 분석해, 내가 팔로우하지만 나를 팔로우하지 않는 계정을 찾아줍니다.")
if st.button("▶️ 인스타 언팔체크 실행하기"):
    st.switch_page("pages/check.py")

st.markdown("\n---")

st.markdown("### 💳 카드값 계산기")
st.write("여러 카드사에서 받은 월별 이용내역을 업로드하면 하나의 통합표로 정리해줍니다.")
if st.button("▶️ 카드값 계산기 실행하기"):
    st.switch_page("pages/cards.py")

st.markdown("\n---")

st.markdown("### 📊 정산 도우미")
st.write("엑셀 파일을 업로드해 BL별 금액 누락 및 불일치를 자동으로 비교합니다.")
if st.button("▶️ 정산 도우미 실행하기"):
    st.switch_page("pages/audit.py")

st.markdown("\n---")
st.markdown("ℹ️ 향후 다양한 도구들이 이곳에 추가될 예정입니다.")
st.caption("© 2025 제니앱 · 문의: id@matt.kr")
