import pandas as pd
from typing import Optional

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Optional[str]:
    try:
        xls = pd.ExcelFile(file)
        file_name = file.name.lower()

        def normalize(text):
            return str(text).replace('\n', '').replace('\r', '').replace(' ', '').strip()

        # 카드사별 시그니처 열 조합
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
        # 시트 이름 유사도 기반 선택
        sheet = next((s for s in xls.sheet_names if "상세" in s), xls.sheet_names[0])
        df = xls.parse(sheet)

        # 필수 컬럼 존재 여부 확인
        required_cols = ["이용일자", "이용가맹점", "업종", "이용금액", "취소여부", "취소금액"]
        if not set(required_cols).issubset(df.columns):
            raise ValueError("필수 열 누락")

        # 취소되지 않은 건만 필터
        df = df[df["취소여부"].str.upper() != "Y"]

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
        
        # 불필요한 행 제거
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
