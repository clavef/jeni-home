# prism.py - 카드사 자동 인식 및 파싱 모듈

import pandas as pd
from typing import Optional

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Optional[str]:
    try:
        xls = pd.ExcelFile(file)
        sheet_names = [name.strip() for name in xls.sheet_names]
        file_name = file.name.lower()

        # 파일명 키워드 기반
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
        if "samsung" in file_name or "삼성" in file_name or "할부" in file_name:
            return "삼성카드"

        # 시트명 기반
        if "■ 국내이용내역" in sheet_names:
            return "삼성카드"

        df_preview = xls.parse(sheet_names[0], nrows=5)
        cols = df_preview.columns.astype(str).str.strip().tolist()
        colset = set(cols)

        print(f"[DEBUG] {file.name} 열 목록:")
        for c in cols:
            print(f"- {c}")

        # 열 조합 기반 인식
        if {"이용일자", "이용가맹점", "업종", "이용금액"}.issubset(colset):
            return "롯데카드"
        if {"이용일", "이용하신곳", "이용카드명", "국내이용금액\n(원)"}.issubset(colset):
            return "KB국민카드"
        if {"거래일자", "이용가맹점", "거래금액"}.issubset(colset):
            return "신한카드"
        if {"이용일", "이용가맹점", "이용금액"}.issubset(colset):
            return "현대카드"
        if {"승인일자", "가맹점명", "승인금액(원)"}.issubset(colset):
            return "삼성카드"
        if {"항목", "구분", "이용일자", "이용금액"}.intersection(colset):
            return "하나카드"

        return None
    except Exception as e:
        print("[ERROR] detect_card_issuer 예외 발생:", e)
        return None
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
