# cards.py (제니앱 - 카드값 계산기)

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from prism import detect_card_issuer, parse_card_file
from shared import show_menu

st.set_page_config(page_title="카드값 계산기 - 제니앱", page_icon="💳", layout="wide")
show_menu("카드값 계산기")

st.title("💳 카드값 계산기")

uploaded_files = st.file_uploader(
    "카드사별 이용 내역 파일 업로드 (여러 개 가능)",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    all_records = []
    for file in uploaded_files:
        card_issuer = detect_card_issuer(file)
        if not card_issuer:
            st.warning(f"❌ 카드사 인식 실패: {file.name}")

            # 디버깅용 열 확인 코드
            st.write(f"📁 {file.name} 열 샘플:")
            try:
                xls = pd.ExcelFile(file)
                for sheet in xls.sheet_names:
                    df = xls.parse(sheet, header=None, nrows=50)
                    st.write(f"📄 Sheet: {sheet}")
                    st.dataframe(df)
            except Exception as e:
                st.error(f"파일 미리보기 오류: {e}")

            continue

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

        # 엑셀 다운로드
        @st.cache_data
        def to_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='카드내역')
            return output.getvalue()

        st.download_button(
            label="📥 엑셀로 다운로드",
            data=to_excel(final_df),
            file_name="카드값_통합내역.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
