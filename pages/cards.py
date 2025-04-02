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
            st.warning(f"⚠️ {card_issuer} 내역 파시마 실패")

if uploaded_files and all_records:
    final_df = pd.concat(all_records, ignore_index=True)

    # ✅ 카드명 정리
    final_df["\uce74\ub4dc"] = final_df["\uce74\ub4dc"].apply(normalize_card_name)

    st.subheader("📋 통합 카드 사용 내역")
    st.dataframe(final_df, use_container_width=True)

    # ✅ 엘셀 다운로드 함수
    @st.cache_data
    def to_excel(df):
        from io import BytesIO
        from openpyxl import Workbook
        from openpyxl.utils.dataframe import dataframe_to_rows
        from openpyxl.styles import Alignment, NamedStyle, numbers

        output = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = '카드내역'

        # 데이터프리마 쓰기
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        # 여름 너비 조정
        col_widths = {
            'A': 11,  # 날짜
            'B': 11,  # 카드
            'C': 20,  # 카테고리
            'D': 40,  # 사용체
            'E': 11,  # 금액
        }
        for col, width in col_widths.items():
            ws.column_dimensions[col].width = width

        # 가능한 포맷 바꾸기 (25.03.29)
        for row in ws.iter_rows(min_row=2, max_col=1):
            for cell in row:
                try:
                    cell.number_format = 'yy.mm.dd'
                except:
                    pass

        # 금액: 숫자지만 포맷은 #,##0 적용
        for row in ws.iter_rows(min_row=2, min_col=5, max_col=5):
            for cell in row:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal='right', vertical='center')

        # 기타 여름: 왼쪽 정렬
        for row in ws.iter_rows(min_row=2, max_col=4):
            for cell in row:
                cell.alignment = Alignment(horizontal='left', vertical='center')

        wb.save(output)
        return output.getvalue()

    st.download_button(
        label="📅 엘셀로 다운로드",
        data=to_excel(final_df),
        file_name="카드값_통합내역.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
