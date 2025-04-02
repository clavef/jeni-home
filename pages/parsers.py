# parsers.py - 카드사 자동 인식 및 파싱 모듈

import pandas as pd
from typing import Optional

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Optional[str]:
    try:
        xls = pd.ExcelFile(file)
        sheet_names = [name.strip() for name in xls.sheet_names]

        if "■ 국내이용내역" in sheet_names:
            return "삼성카드"
        if any("롯데" in sheet for sheet in sheet_names):
            return "롯데카드"
        if any("신한" in sheet for sheet in sheet_names):
            return "신한카드"
        if any("현대" in sheet for sheet in sheet_names):
            return "현대카드"
        if any("하나" in sheet or "이용상세내역" in sheet for sheet in sheet_names):
            return "하나카드"
        if any("KB국민" in sheet or "국민카드" in sheet for sheet in sheet_names):
            return "KB국민카드"

        # 시트명 외에도 본문 열 기반 추가 탐지 로직
        df_preview = xls.parse(sheet_names[0], nrows=5)
        cols = df_preview.columns.astype(str).str.lower().tolist()

        if any("myshinhancard" in c or "마이신한" in c for c in cols):
            return "신한카드"
        if any("롯데" in c for c in cols):
            return "롯데카드"
        if any("현대" in c for c in cols):
            return "현대카드"
        if any("네이버페이" in c or "kcp" in c for c in cols):
            return "현대카드"
        if any("kb국민" in c or "위시" in c for c in cols):
            return "KB국민카드"

        return None
    except Exception:
        return None

# --- 롯데카드 파서 예시 ---
def parse_card_file(file, issuer: str) -> Optional[pd.DataFrame]:
    if issuer == "롯데카드":
        return parse_lotte(file)
    # 향후 다른 카드사별 파서 추가 예정
    return None

def parse_lotte(file):
    try:
        xls = pd.ExcelFile(file)
        df = xls.parse("■ 국내이용내역", skiprows=6)
        df = df[["이용일자", "이용가맹점", "업종", "이용금액"]]
        df.columns = ["날짜", "사용처", "카테고리", "금액"]
        df["카드"] = "롯데카드"
        df = df[["날짜", "카드", "카테고리", "사용처", "금액"]]
        return df
    except Exception as e:
        print("롯데카드 파싱 오류:", e)
        return None
