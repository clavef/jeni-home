# parsers.py - 카드사 자동 인식 및 파싱 모듈

import pandas as pd
from typing import Optional

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Optional[str]:
    try:
        xls = pd.ExcelFile(file)
        sheet_names = [name.strip() for name in xls.sheet_names]

        file_name = file.name.lower()
        if "lotte" in file_name or "veex" in file_name:
            return "롯데카드"
        if "shinhan" in file_name or "신한" in file_name:
            return "신한카드"
        if "hyundai" in file_name or "현대" in file_name:
            return "현대카드"
        if "hana" in file_name or "이용상세내역" in file_name:
            return "하나카드"
        if "kb" in file_name or "국민" in file_name:
            return "KB국민카드"
        if "삼성" in file_name or "할부" in file_name:
            return "삼성카드"

        if "■ 국내이용내역" in sheet_names:
            return "삼성카드"

        df_preview = xls.parse(sheet_names[0], nrows=5)
        cols = df_preview.columns.astype(str).str.lower().tolist()

        if any("가맹점명" in c and "승인" in c for c in cols):
            return "삼성카드"
        if any("이용가맹점" in c for c in cols) and any("veex" in str(xls.parse(sheet_names[0]).to_string()).lower()):
            return "롯데카드"
        if any("이용카드명" in c for c in cols) and any("kb국민" in str(xls.parse(sheet_names[0]).to_string()).lower()):
            return "KB국민카드"
        if any("네이버페이" in str(xls.parse(sheet_names[0]).to_string()).lower()):
            return "현대카드"
        if any("준디지털" in str(xls.parse(sheet_names[0]).to_string()).lower()):
            return "신한카드"
        if any("이용상세내역" in sheet.lower() for sheet in sheet_names):
            return "하나카드"

        return None
    except Exception:
        return None

# --- 카드사별 파서 연결 ---
def parse_card_file(file, issuer: str) -> Optional[pd.DataFrame]:
    if issuer == "롯데카드":
        return parse_lotte(file)
    if issuer == "KB국민카드":
        return parse_kb(file)
    if issuer == "신한카드":
        return parse_shinhan(file)
    if issuer == "현대카드":
        return parse_hyundai(file)
    if issuer == "하나카드":
        return parse_hana(file)
    if issuer == "삼성카드":
        return parse_samsung(file)
    return None

# 이하 파싱 함수 동일 (생략)...
