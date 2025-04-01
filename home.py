import streamlit as st
from PIL import Image

def main():
    st.set_page_config(page_title="제니앱 (Jeni.kr)", layout="centered")

    st.title("🎯 제니앱 (Jeni.kr)")
    st.markdown("**업무 효율을 높이는 실용적인 도구들을 한곳에, 제니앱에서 만나보세요.**")
    st.markdown("---")

    st.markdown("### ✅ SNC-KZ 정산 도우미")
    st.write("엑셀 파일을 업로드해 BL별 금액 누락 및 불일치를 자동으로 비교합니다.")
    st.markdown("""
        <a href="#" onclick="window.open('https://jeni-kz.streamlit.app', '_blank', 'width=1100,height=800'); return false;">
            <button style='padding:10px 20px; font-size:16px;'>앱 실행하기</button>
        </a>
    """, unsafe_allow_html=True)

    st.markdown("\n\n---")
    st.markdown("ℹ️ 향후 다양한 업무 보조 도구가 이곳에 추가될 예정입니다.")
    st.caption("© 2025 제니앱 · 문의: id@matt.kr")

if __name__ == "__main__":
    main()
