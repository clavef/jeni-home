# prism.py - 롯데카드 파싱 개선 + 하나카드 추가 판별 로직

import pandas as pd
from typing import Optional, Tuple

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Tuple[list, Optional[str]]:
    logs = []
    try:
        xls = pd.ExcelFile(file)

        def normalize(text):
            return str(text).replace('\n', '').replace('\r', '').replace(' ', '').strip()

        def fuzzy_match(columns, keywords):
            return all(any(k in col for col in columns) for k in keywords)

        patterns = {
            "롯데카드": ["이용일자", "이용가맹점", "업종", "이용금액"],
            "KB국민카드": ["이용일", "이용하신곳", "이용카드명", "국내이용금액"],
            "신한카드": ["거래일자", "이용가맹점", "거래금액"],
            "현대카드": ["이용일", "이용가맹점", "이용금액"],
            "삼성카드": ["승인일자", "가맹점명", "승인금액"],
            "하나카드": ["거래일자", "가맹점명", "이용금액"],
        }

        logs.append(f"📁 파일명: {file.name}")

        for sheet in xls.sheet_names:
            df = xls.parse(sheet, header=None)
            logs.append(f"📄 시트: {sheet}")
            for i in range(len(df)):
                row = df.iloc[i]
                normed = [normalize(cell) for cell in row if pd.notna(cell)]
                if not normed:
                    continue
                logs.append(f"🧩 행 {i}: {normed}")
                for issuer, keywords in patterns.items():
                    if fuzzy_match(normed, keywords):
                        # 신한/하나카드 키워드가 동일하므로 정교하게 판단
                        if issuer == "신한카드" and set(keywords) == set(patterns["하나카드"]):
                            file_text = "".join([str(cell) for r in df.values for cell in r if pd.notna(cell)]).lower()
                            if "하나" in file.name.lower() or "하나카드" in file_text:
                                logs.append(f"✅ 인식됨: 하나카드 (행 {i})")
                                return logs, "하나카드"
                        logs.append(f"✅ 인식됨: {issuer} (행 {i})")
                        return logs, issuer

        logs.append("❌ 어떤 카드사도 인식되지 않음")
        return logs, None
    except Exception as e:
        logs.append(f"[ERROR] detect_card_issuer 예외 발생: {e}")
        return logs, None

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
        for sheet in xls.sheet_names:
            df = xls.parse(sheet, header=None)
            for i in range(len(df)):
                row = df.iloc[i].dropna().astype(str).tolist()
                if {"이용일자", "이용가맹점", "업종", "이용금액"}.issubset(set(row)):
                    df = xls.parse(sheet, skiprows=i)
                    df = df[["이용일자", "이용가맹점", "업종", "이용금액"]]
                    df.columns = ["날짜", "사용처", "카테고리", "금액"]
                    df["카드"] = "롯데카드"
                    return df[["날짜", "카드", "카테고리", "사용처", "금액"]]
        return None
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
