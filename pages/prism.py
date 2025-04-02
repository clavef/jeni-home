# pages/prism.py

import streamlit as st
import pandas as pd
from typing import Optional

# ✅ 직접 실행된 경우에만 경고 메시지 출력
if __name__ == "__main__" or st.runtime.exists():
    st.set_page_config(page_title="내부 함수 (Prism)", layout="centered")
    st.warning("⚠️ 이 페이지는 내부 기능을 위한 페이지입니다. 직접 사용할 필요는 없습니다.")

# --- 카드사 자동 인식 ---
def detect_card_issuer(file) -> Optional[str]:
    try:
        xls = pd.ExcelFile(file)

        def normalize(text):
            return str(text).replace('\n', '').replace('\r', '').replace(' ', '').strip()

        patterns = {
            "롯데카드": {"이용일자", "이용가맹점", "업종", "이용금액"},
            "KB국민카드": {"이용일", "이용하신곳", "이용카드명", "국내이용금액(원)"},
            "신한카드": {"거래일자", "이용가맹점", "거래금액"},
            "현대카드": {"이용일", "이용가맹점", "이용금액"},
            "삼성카드": {"승인일자", "가맹점명", "승인금액(원)"},
            "하나카드": {"거래일자", "가맹점명", "이용금액"},
        }

        for sheet in xls.sheet_names:
            df = xls.parse(sheet, header=None)
            for i in range(min(100, len(df))):
                row = df.iloc[i]
                normed = set(normalize(cell) for cell in row if pd.notna(cell))
                for issuer, keywords in patterns.items():
                    if keywords.issubset(normed):
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
        import pandas as pd

        xls = pd.ExcelFile(file)
        sheet = xls.sheet_names[0]
        df = xls.parse(sheet, skiprows=6)

        # ❗ 승인취소 / 취소전표매입 제외
        if "상태" in df.columns:
            df = df[~df["상태"].astype(str).str.contains("승인취소|취소전표", na=False)]

        # ✅ 필요한 컬럼만 추출
        df = df[["이용일", "이용하신곳", "이용카드명", "국내이용금액\n(원)", "결제방법"]]
        df.columns = ["날짜", "사용처", "카드", "금액", "결제방법"]

        # ✅ 날짜 형식 통일
        df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.strftime("%Y.%m.%d")

        # ✅ 금액 숫자 처리
        df["금액"] = df["금액"].astype(str).str.replace(",", "").astype(int)

        # ✅ 할부인 경우 → 이번달 결제금액만 포함
        def adjust_installment(row):
            method = str(row["결제방법"])
            if method != "일시불" and any(char.isdigit() for char in method):
                months = int(''.join(filter(str.isdigit, method)))
                return round(row["금액"] / months)
            else:
                return row["금액"]

        df["금액"] = df.apply(adjust_installment, axis=1)

        df["카테고리"] = ""

        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]

    except Exception as e:
        print("KB국민카드 파싱 오류:", e)
        return None

# --- 신한카드 ---
def parse_shinhan(file):
    try:
        import pandas as pd

        xls = pd.ExcelFile(file)
        sheet = xls.sheet_names[0]
        df = xls.parse(sheet, skiprows=2)

        # ✅ 필수 컬럼만 선택
        df = df[["거래일자", "이용가맹점", "결제 금액"]]
        df.columns = ["날짜", "사용처", "금액"]

        # ✅ 숫자 포맷 정리
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce")

        df["카드"] = "신한카드"
        df["카테고리"] = ""

        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]

    except Exception as e:
        print("신한카드 파싱 오류:", e)
        return None

# --- 현대카드 ---
def parse_hyundai(file):
    import pandas as pd

    try:
        xls = pd.ExcelFile(file)
        sheet = xls.sheet_names[0]
        df = xls.parse(sheet, skiprows=2)

        # ✅ 소계·합계 등 제거
        df = df[~df["이용가맹점"].astype(str).str.contains("합계|소계|총|이월", na=False)]

        # ✅ 엑셀 시리얼 날짜 복원: 숫자 or 숫자 문자열도 포함
        def convert_excel_date(val):
            try:
                val = float(val)
                return pd.to_datetime("1899-12-30") + pd.to_timedelta(val, unit="D")
            except:
                return pd.to_datetime(val, errors="coerce")

        df["이용일"] = df["이용일"].apply(convert_excel_date)
        df["이용일"] = df["이용일"].dt.strftime("%Y.%m.%d")  # 보기 좋게 포맷

        # ✅ 필요한 컬럼만 추출
        df = df[["이용일", "이용가맹점", "이용금액"]].copy()
        df.columns = ["날짜", "사용처", "금액"]
        df["카드"] = "현대카드"
        df["카테고리"] = ""

        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]

    except Exception as e:
        print("현대카드 파싱 오류:", e)
        return None

# --- 하나카드 ---
def parse_hana(file):
    import re
    import pandas as pd

    def is_date_like(val):
        try:
            if pd.isna(val):
                return False
            val_str = str(val).strip()
            return bool(re.match(r"\d{4}\.\d{2}\.\d{2}", val_str))
        except:
            return False

    try:
        xls = pd.ExcelFile(file)
        sheet_name = xls.sheet_names[0]

        df = xls.parse(sheet_name, skiprows=28)
        df.columns = df.columns.astype(str).str.replace('\n', '').str.replace(' ', '').str.strip()

        if not {"거래일자", "가맹점명", "이용금액"}.issubset(df.columns):
            return None

        df = df[["거래일자", "가맹점명", "이용금액"]].copy()
        df.columns = ["날짜", "사용처", "금액"]
        df["카드"] = "하나카드"
        df["카테고리"] = ""

        df = df[df["날짜"].apply(is_date_like)]

        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]

    except Exception:
        return None

# --- 삼성카드 ---
def parse_samsung(file):
    try:
        import pandas as pd

        xls = pd.ExcelFile(file)
        df = xls.parse(xls.sheet_names[1])  # 두 번째 시트

        # 필요한 열만 추출
        df = df[["승인일자", "승인시각", "가맹점명", "승인금액(원)"]].dropna()

        # 승인금액 정수형으로 변환
        df["승인금액(원)"] = df["승인금액(원)"].astype(str).str.replace(",", "").astype(int)

        # 매칭 키 생성 (승인일자 + 승인시각 + 금액 절댓값)
        df["매칭키"] = (
            df["승인일자"].astype(str) + "_" +
            df["승인시각"].astype(str) + "_" +
            df["승인금액(원)"].abs().astype(str)
        )

        # 중복된 +, - 쌍 제거
        dupes = df[df.duplicated("매칭키", keep=False)]
        to_remove = dupes.groupby("매칭키").filter(
            lambda g: (g["승인금액(원)"] > 0).any() and (g["승인금액(원)"] < 0).any()
        )
        df = df[~df.index.isin(to_remove.index)]

        # 표준 포맷 구성
        df["날짜"] = pd.to_datetime(df["승인일자"]).dt.strftime("%Y.%m.%d")
        df["카드"] = "삼성카드"
        df["사용처"] = df["가맹점명"]
        df["금액"] = df["승인금액(원)"]
        df["카테고리"] = ""

        return df[["날짜", "카드", "카테고리", "사용처", "금액"]]

    except Exception as e:
        print("삼성카드 파싱 오류:", e)
        return None
