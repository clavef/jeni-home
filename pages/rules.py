import re

# ✅ 간단한 규칙 기반 자동 분류 함수
def categorize(merchant: str) -> str:
    merchant = str(merchant)

    # ✅ 우선 적용 규칙 (상위 우선순위)
    high_priority_rules = [
        (r"주차장", "교통/주유/주차"),  # 주차장이 포함되면 우선
        (r"롯데마트|달콤N|매머드|헤이듀", "음식점/카페/편의점"),  # 단 '주차장'보다 우선순위 낮음
        (r"기프티샷|백화점", "취미/쇼핑"),
        (r"파킹|빌딩관리단|티머니|택시", "교통/주유/주차"),
        (r"KCP|보람상조|효성에프엠에스|Microsoft", "고정지출"),
        (r"\(주\)다날\s*-\s*카카오", "고정지출"),
    ]

    # ✅ 일반 규칙
    general_rules = [
        (r"주유|충전|자동차|세차|오토오아시스|주차", "교통/주유/주차"),
        (r"병원|치과|의원|내과|약국|정형외과", "병원/약국"),
        (r"네이버페이|페이코|PAYPAL|기프티콘|쇼핑|디지털|전자|마켓|Temu|쿠팡|위메프|G마켓|11번가|인터파크|스마트스토어|번개장터", "취미/쇼핑"),
        (r"카페|커피|이디야|스타벅스|편의점|씨유|CU|GS25|세븐일레븐|emart24|올리브영|식당|음식|한솥|고기|김밥|카카오|배달", "음식점/카페/편의점"),
        (r"관리비|통신|SKT|KT|LGU\+|렌탈|보험|납부|세금|등록금|교육비|마이데이터|고정지출", "고정지출"),
    ]

    # ✅ 우선 규칙 먼저 적용
    for pattern, category in high_priority_rules:
        if re.search(pattern, merchant, re.IGNORECASE):
            return category

    # ✅ 일반 규칙 적용
    for pattern, category in general_rules:
        if re.search(pattern, merchant, re.IGNORECASE):
            return category

    return "잡비용"
