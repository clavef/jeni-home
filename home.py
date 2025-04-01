import streamlit as st

def main():
    st.set_page_config(page_title="제니앱 도구 모음", layout="centered")

    st.title("🧰 제니앱 도구 모음")
    st.markdown("---")

    st.markdown("### ✅ SNC-KZ 정산 도우미")
    st.write("엑셀 파일을 업로드해 BL별 금액 누락 및 불일치를 자동으로 비교합니다.")
    st.link_button("앱 실행하기", url="https://snc-kz-checker.streamlit.app/", use_container_width=True)

    st.markdown("\n\n---")
    st.markdown("ℹ️ 향후 다양한 업무 보조 도구가 이곳에 추가될 예정입니다.")
    st.caption("문의: id@matt.kr")

if __name__ == "__main__":
    main()
