# cards.py (제니앱 - 카드값 계산기)

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from prism import detect_card_issuer, parse_card_file
from shared import show_menu
from rules import categorize

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

    # ✅ 업로드 결과 메시지 10개까지 한 페이지에 보이도록 컨테이너 사용
    with st.container():
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

    if all_records:
        final_df = pd.concat(all_records, ignore_index=True)
        final_df["카드"] = final_df["카드"].apply(normalize_card_name)
        final_df["카테고리"] = final_df["사용처"].apply(categorize)

        # ✅ 정렬 순서: 카드 → 카테고리 → 날짜
        final_df = final_df.sort_values(by=["카드", "카테고리", "날짜"]).reset_index(drop=True)

        st.subheader("📋 통합 카드 사용 내역")
        st.dataframe(final_df, use_container_width=True)

        # ✅ 엑셀 다운로드 함수
        @st.cache_data
        def to_excel(df):
            from io import BytesIO
            from openpyxl import Workbook
            from openpyxl.utils.dataframe import dataframe_to_rows
            from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
            from openpyxl.worksheet.page import PageMargins
            from openpyxl.worksheet.properties import WorksheetProperties, PageSetupProperties

            output = BytesIO()
            wb = Workbook()
            ws = wb.active
            ws.title = '카드내역'

            color_map_card = {
                "국민카드": "FBE2D5",
                "현대카드": "DDEBF7",
                "롯데카드": "CCCCFF",
                "삼성카드": "E2EFDA",
                "하나카드": "FFF2CC",
            }

            color_map_category = {
                "교통/주유/주차": "CCFFCC",
                "병원/약국": "FFCC99",
                "취미/쇼핑": "FFF2CC",
                "음식점/카페/편의점": "FFCCCC",
                "고정지출": "C6E0B4",
                "잡비용": "E7E6E6",
            }

            thin_border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin')
            )

            # 헤더
            ws.append(df.columns.tolist())
            for cell in ws[1]:
                cell.fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # 데이터
            for row in dataframe_to_rows(df, index=False, header=False):
                ws.append(row)

            # 열 너비
            col_widths = [11, 11, 20, 40, 11]
            for i, width in enumerate(col_widths):
                ws.column_dimensions[chr(65 + i)].width = width

            # 눈금선 제거
            ws.sheet_view.showGridLines = False

            # 셀 스타일
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                card = row[1].value
                category = row[2].value
                card_color = color_map_card.get(card, None)
                category_color = color_map_category.get(category, None)

                for idx, cell in enumerate(row):
                    cell.border = thin_border
                    if idx == 4:  # 금액
                        try:
                            cell.number_format = '#,##0'
                            cell.alignment = Alignment(horizontal="right", vertical="center")
                            cell.value = int(str(cell.value).replace(',', ''))
                        except:
                            pass
                    else:
                        cell.alignment = Alignment(horizontal="left", vertical="center")

                if card_color:
                    row[0].fill = PatternFill(start_color=card_color, end_color=card_color, fill_type="solid")
                    row[1].fill = PatternFill(start_color=card_color, end_color=card_color, fill_type="solid")
                if category_color:
                    row[2].fill = PatternFill(start_color=category_color, end_color=category_color, fill_type="solid")

            # 페이지 설정
            ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.75, bottom=0.75)
            ws.sheet_properties = WorksheetProperties(pageSetUpPr=PageSetupProperties(fitToPage=True))

            wb.save(output)
            return output.getvalue()

        st.download_button(
            label="📥 엑셀로 다운로드",
            data=to_excel(final_df),
            file_name="카드값_통합내역.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
