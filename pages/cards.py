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

# ✅ 카드명 정규화 함수
def normalize_card_name(card):
    if "국민" in card:
        return "국민카드"
    if "신한" in card:
        return "신한카드"
    if "현대" in card:
        return "현대카드"
    if "하나" in card:
        return "하나카드"
    if "롯데" in card:
        return "롯데카드"
    if "삼성" in card:
        return "삼성카드"
    return card

if uploaded_files:
    all_records = []
    for file in uploaded_files:
        st.markdown(f"---\n### 📂 {file.name}")

        card_issuer = detect_card_issuer(file)
       
        if not card_issuer:
            st.warning(f"❌ 카드사 인식 실패: {file.name}")
            continue

        df = parse_card_file(file, card_issuer)
        if df is not None:
            all_records.append(df)
            st.success(f"✅ {card_issuer} 내역 처리 완료: {len(df)}건")
        else:
            st.warning(f"⚠️ {card_issuer} 내역 파싱 실패")

if uploaded_files and all_records:
    final_df = pd.concat(all_records, ignore_index=True)

    # ✅ 카드명 정리
    final_df["카드"] = final_df["카드"].apply(normalize_card_name)

    # ✅ 금액 쉼표 표시
    final_df["금액"] = final_df["금액"].apply(lambda x: f"{int(x):,}")

    st.subheader("📋 통합 카드 사용 내역")
    st.dataframe(final_df, use_container_width=True)

    # ✅ 엑셀 다운로드 함수
    @st.cache_data
    def to_excel(df):
        from io import BytesIO
        from openpyxl import Workbook
        from openpyxl.utils.dataframe import dataframe_to_rows
        from openpyxl.styles import Alignment

        output = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = '카드내역'

        # 데이터프레임 쓰기
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        # 열 너비 조정
        col_widths = {
            'A': 11,  # 날짜
            'B': 11,  # 카드
            'C': 20,  # 카테고리
            'D': 40,  # 사용처
            'E': 11,  # 금액
        }
        for col, width in col_widths.items():
            ws.column_dimensions[col].width = width

        # 정렬
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(horizontal='left', vertical='center')

        wb.save(output)
        return output.getvalue()

    st.download_button(
        label="📥 엑셀로 다운로드",
        data=to_excel(final_df),
        file_name="카드값_통합내역.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
