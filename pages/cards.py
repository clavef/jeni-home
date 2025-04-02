import streamlit as st
from prism import detect_card_issuer, parse_card_file

# 파일 업로드
uploaded_files = st.file_uploader("📂 카드사 파일을 업로드하세요.", type=["xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        # 카드사 인식
        card_issuer = detect_card_issuer(file)
        
        if card_issuer:
            st.success(f"✅ {file.name} - {card_issuer} 카드 내역 처리 완료!")
            # 카드사별 파일 파싱
            df = parse_card_file(file, card_issuer)
            if df is not None:
                st.dataframe(df)
            else:
                st.warning(f"⚠️ {card_issuer} 카드 내역 파싱 실패!")
        else:
            st.error(f"❌ {file.name} - 카드사 인식 실패!")
