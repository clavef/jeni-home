import streamlit as st
import pandas as pd
from prism import detect_card_issuer, parse_card_file
from shared import show_menu  # 왼쪽 메뉴 추가

# 메뉴 표시
show_menu("카드값 계산기")

st.title("💳 카드값 계산기")

uploaded_files = st.file_uploader("카드사별 이용 내역 파일 업로드 (여러 개 가능)",
                                   type=["xlsx"],
                                   accept_multiple_files=True)

if uploaded_files:
    all_records = []
    for file in uploaded_files:
        card_issuer = detect_card_issuer(file)
        if not card_issuer:
            st.warning(f"❌ 카드사 인식 실패: {file.name}")
            continue  # 카드사 인식 실패 메시지 출력

        df = parse_card_file(file, card_issuer)
        if df is not None:
            all_records.append(df)
            st.success(f"✅ {card_issuer} 내역 처리 완료: {len(df)}건")
        else:
            st.warning(f"⚠️ {card_issuer} 내역 파싱 실패")

    if all_records:
        final_df = pd.concat(all_records, ignore_index=True)
        st.subheader("📋 통합 카드 사용 내역")
        st.dataframe(final_df, use_container_width=True)

        # 엑셀 다운로드 (캐시 없이 실행)
        def to_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='카드내역')
            return output.getvalue()

        st.download_button(
            label="📥 엑셀로 다운로드",
            data=to_excel(final_df),
            file_name="카드값_통합내역.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
