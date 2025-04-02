import pandas as pd
from typing import Optional

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Optional[str]:
    try:
        xls = pd.ExcelFile(file)
        file_name = file.name.lower()

        def normalize(text):
            return str(text).replace('\n', '').replace('\r', '').replace(' ', '').strip()

        patterns = {
            "롯데카드": {"이용일자", "이용가맹점", "업종", "이용금액"},
            "KB국민카드": {"이용일", "이용하신곳", "이용카드명", "국내이용금액(원)"},
            "신한카드": {"거래일자", "이용가맹점", "거래금액"},
            "현대카드": {"이용일", "이용가맹점", "이용금액"},
            "삼성카드": {"승인일자", "가맹점명", "승인금액(원)"},
            "하나카드": {"항목", "구분", "날짜", "사용처", "금액"},
        }

        for sheet in xls.sheet_names:
            df = xls.parse(sheet, header=None)
            for i in range(len(df)):
                row = df.iloc[i]
                normed = set(normalize(cell) for cell in row if pd.notna(cell))
                for issuer, keywords in patterns.items():
                    if keywords <= normed:
                        return issuer

        return None
    except Exception as e:
        print("[ERROR] detect_card_issuer 예외 발생:", e)
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

# --- 롯데카드 디버깅용 ---
def parse_lotte_debug(file):
    import streamlit as st
    try:
        xls = pd.ExcelFile(file)

        st.write("📄 시트 목록:", xls.sheet_names)

        sheet_name = xls.sheet_names[0]
        st.write(f"✅ 선택된 시트: `{sheet_name}`")

        df = xls.parse(sheet_name, skiprows=2)
        df.columns = df.columns.str.strip()
        st.write("📊 전체 컬럼 목록:", df.columns.tolist())
        st.write("🔍 데이터 미리보기", df.head())

        return df
    except Exception as e:
        st.error(f"❌ 롯데카드 디버깅 실패: {e}")
        return None

# --- 롯데카드 ---
def parse_lotte(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_name = xls.sheet_names[0]

        # ✅ skiprows를 8로 조정해서 실제 헤더가 나오는 줄에 맞춤
        df = xls.parse(sheet_name, skiprows=8)
        df.columns = df.columns.str.strip()

        # ✅ 필요 컬럼 존재 여부 확인
        required_cols = ["이용일자", "이용가맹점", "업종", "이용금액", "취소여부"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"[롯데카드] 누락된 필수 컬럼: {missing}")
            return None

        # ✅ 취소 거래 제외
        df = df[df["취소여부"].astype(str).str.upper() != "Y"]

        # ✅ 필요한 컬럼만 추출하고 포맷 통일
        df = df[["이용일자", "이용가맹점", "업종", "이용금액"]].copy()
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
        df = df[~df["날짜"].str.contains("하나카드|포인트|이벤트", na=False)]

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
