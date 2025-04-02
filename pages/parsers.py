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

# --- 롯데카드 ---
def parse_lotte(file):
    try:
        xls = pd.ExcelFile(file)
        df = xls.parse("■ 국내이용내역", skiprows=6)
        df = df[["이용일자", "이용가맹점", "업종", "이용금액"]]
        df.columns = ["날짜", "사용처", "카테고리", "금액"]
        df["카드"] = "롯데카드"
        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
    except Exception as e:
        print("롯데카드 파싱 오류:", e)
        return None

# --- KB국민카드 ---
def parse_kb(file):
    try:
        xls = pd.ExcelFile(file)
        sheet = xls.sheet_names[0]
        df = xls.parse(sheet, skiprows=6)
        df = df[["이용일", "이용하신곳", "이용카드명", "국내이용금액\n(원)"]]
        df.columns = ["날짜", "사용처", "카드", "금액"]
        df["카테고리"] = ""
        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
    except Exception as e:
        print("KB국민카드 파싱 오류:", e)
        return None

# --- 신한카드 ---
def parse_shinhan(file):
    try:
        xls = pd.ExcelFile(file)
        sheet = xls.sheet_names[0]
        df = xls.parse(sheet, skiprows=2)
        df = df[["거래일자", "이용가맹점", "거래금액"]]
        df.columns = ["날짜", "사용처", "금액"]
        df["카드"] = "신한카드"
        df["카테고리"] = ""
        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
    except Exception as e:
        print("신한카드 파싱 오류:", e)
        return None

# --- 현대카드 ---
def parse_hyundai(file):
    try:
        xls = pd.ExcelFile(file)
        sheet = xls.sheet_names[0]
        df = xls.parse(sheet, skiprows=2)
        df = df[["이용일", "이용가맹점", "이용금액"]]
        df.columns = ["날짜", "사용처", "금액"]
        df["카드"] = "현대카드"
        df["카테고리"] = ""
        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
    except Exception as e:
        print("현대카드 파싱 오류:", e)
        return None

# --- 하나카드 ---
def parse_hana(file):
    try:
        xls = pd.ExcelFile(file)
        for sheet in xls.sheet_names:
            if "상세" in sheet:
                df = xls.parse(sheet, skiprows=9)
                break
        else:
            df = xls.parse(xls.sheet_names[0], skiprows=9)

        df = df.dropna(subset=[df.columns[0]])
        df = df.iloc[:, :5]
        df.columns = ["항목", "구분", "날짜", "사용처", "금액"]
        df["카드"] = "하나카드"
        df["카테고리"] = df["구분"]
        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
    except Exception as e:
        print("하나카드 파싱 오류:", e)
        return None

# --- 삼성카드 ---
def parse_samsung(file):
    try:
        xls = pd.ExcelFile(file)
        df = xls.parse("■ 국내이용내역")
        df = df[["승인일자", "가맹점명", "승인금액(원)"]]
        df.columns = ["날짜", "사용처", "금액"]
        df["카드"] = "삼성카드"
        df["카테고리"] = ""
        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
    except Exception as e:
        print("삼성카드 파싱 오류:", e)
        return None
