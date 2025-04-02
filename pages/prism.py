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

# --- 롯데카드 ---
def parse_lotte(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_name = xls.sheet_names[0]

        # 1차 전체 시트를 헤더 없이 불러오기
        raw = xls.parse(sheet_name, header=None)

        # 필수 헤더 키워드
        header_keywords = {"이용일자", "이용가맹점", "업종", "이용금액"}

        header_row_idx = None
        for i, row in raw.iterrows():
            cells = [str(c).strip() for c in row if pd.notna(c)]
            if header_keywords.issubset(set(cells)):
                header_row_idx = i
                break

        if header_row_idx is None:
            print("[롯데카드] 헤더 행을 찾을 수 없습니다.")
            return None

        # 해당 행부터 정식으로 파싱
        df = xls.parse(sheet_name, skiprows=header_row_idx)
        df.columns = df.columns.str.strip()

        # 취소여부 필드가 없을 수도 있으므로 조건 분기
        if "취소여부" in df.columns:
            df = df[df["취소여부"].astype(str).str.upper() != "Y"]

        # 필요한 컬럼 필터링
        required_cols = ["이용일자", "이용가맹점", "업종", "이용금액"]
        if not set(required_cols).issubset(df.columns):
            print("[롯데카드] 필수 컬럼이 누락되었습니다.")
            return None

        df = df[required_cols].copy()
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
        sheet_name = xls.sheet_names[0]
        raw = xls.parse(sheet_name, header=None)

        # 헤더 키워드 기반 탐색
        header_keywords = {"거래일자", "가맹점명", "이용금액"}
        header_row_idx = None
        for i, row in raw.iterrows():
            cells = [str(c).strip() for c in row if pd.notna(c)]
            if header_keywords.issubset(set(cells)):
                header_row_idx = i
                break

        if header_row_idx is None:
            print("[하나카드] 헤더를 찾을 수 없습니다.")
            return None

        # 헤더 행부터 정식 파싱
        df = xls.parse(sheet_name, skiprows=header_row_idx)
        df.columns = df.columns.str.strip()

        # 필수 열 확인
        required_cols = ["거래일자", "가맹점명", "이용금액"]
        if not set(required_cols).issubset(df.columns):
            print("[하나카드] 필수 컬럼이 없습니다.")
            return None

        df = df[["거래일자", "가맹점명", "이용금액"]].copy()
        df.columns = ["날짜", "사용처", "금액"]
        df["카드"] = "하나카드"
        df["카테고리"] = ""

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
