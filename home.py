import streamlit as st

st.set_page_config(page_title="제니앱 (Jeni.kr)", page_icon="🎯", layout="wide")

st.sidebar.title("🧭 제니앱 메뉴")
st.sidebar.page_link("home.py", label="홈")
st.sidebar.page_link("pages/1_audit.py", label="SNC-KZ 정산 도우미")

st.title("🎯 제니앱 (Jeni.kr)")
st.markdown("**생활과 업무를 편리하게 만들어주는 다양한 도구들을 제니앱에서 만나보세요.**")
st.markdown("---")

st.markdown("### ✅ SNC-KZ 정산 도우미")
st.write("엑셀 파일을 업로드해 BL별 금액 누락 및 불일치를 자동으로 비교합니다.")
st.markdown("왼쪽 메뉴에서 **SNC-KZ 정산 도우미**를 선택하세요.")

st.markdown("\n\n---")
st.markdown("ℹ️ 향후 다양한 도구들이 이곳에 추가될 예정입니다.")
st.caption("© 2025 제니앱 · 문의: id@matt.kr")
