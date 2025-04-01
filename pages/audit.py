# pages/audit.py
import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
from shared import show_menu

show_menu("정산 도우미")

st.title("✅ 정산 도우미")
st.write("KZ와 SNC의 엑셀 파일을 업로드하여 MBL별 금액 비교 결과를 확인하세요.")

file_kz = st.file_uploader("KZ 엑셀 파일 업로드 (.xlsx)", type=["xlsx"], key="kz")
file_snc = st.file_uploader("SNC 엑셀 파일 업로드 (.xlsx)", type=["xlsx"], key="snc")

# 수동 입력 필드
manual_kz = st.number_input("KZ 미승인 금액 수동 입력 (원)", min_value=0, value=0, step=10000, format="%d")

if file_kz and file_snc:
    try:
        df_kz = pd.read_excel(file_kz)
        df_snc = pd.read_excel(file_snc)

        if not {'M.BL#', '승인금액'}.issubset(df_kz.columns):
            st.error("❌ KZ 파일에 'M.BL#' 또는 '승인금액' 열이 없습니다.")
            st.stop()
        if not {'H.B/L NO', 'Unnamed: 11'}.issubset(df_snc.columns):
            st.error("❌ SNC 파일에 'H.B/L NO' 또는 'Unnamed: 11' 열이 없습니다.")
            st.stop()

        df_kz = df_kz[['M.BL#', '승인금액']].copy()
        df_kz.columns = ['MBL', '승인금액']
        df_kz.dropna(subset=['MBL'], inplace=True)
        df_kz['MBL'] = df_kz['MBL'].astype(str).str.strip()
        df_kz['승인금액'] = pd.to_numeric(df_kz['승인금액'], errors='coerce').fillna(0)

        df_snc = df_snc[['H.B/L NO', 'Unnamed: 11']].copy()
        df_snc.columns = ['MBL', '금액_SNC']
        df_snc.dropna(subset=['MBL'], inplace=True)
        df_snc['MBL'] = df_snc['MBL'].astype(str).str.strip()
        df_snc['금액_SNC'] = pd.to_numeric(df_snc['금액_SNC'], errors='coerce').fillna(0)

        all_mbls = pd.Series(sorted(set(df_kz['MBL']) | set(df_snc['MBL'])), name='MBL')

        kz_grouped = df_kz.groupby('MBL')['승인금액'].apply(lambda x: sorted(x.tolist())).reset_index()
        snc_grouped = df_snc.groupby('MBL')['금액_SNC'].apply(lambda x: sorted(x.tolist())).reset_index()

        compare_df = pd.merge(all_mbls.to_frame(), kz_grouped, on='MBL', how='left')
        compare_df = pd.merge(compare_df, snc_grouped, on='MBL', how='left')

        def compare_lists(kz_list, snc_list):
            if not isinstance(kz_list, list): return 'KZ 미승인'
            if not isinstance(snc_list, list): return 'SNC 미입력'
            return '일치' if sorted(kz_list) == sorted(snc_list) else '금액 불일치'

        compare_df['비고'] = compare_df.apply(lambda row: compare_lists(row['승인금액'], row['금액_SNC']), axis=1)
        result_df = compare_df[compare_df['비고'] != '일치'].sort_values(by='MBL')
        result_df.columns = ['MBL#', 'KZ금액', 'SNC금액', '비고']

        result_df.insert(0, '번호', range(1, len(result_df) + 1))

        kz_total = sum([sum(x) if isinstance(x, list) else 0 for x in compare_df['승인금액']]) + manual_kz
        snc_total = sum([sum(x) if isinstance(x, list) else 0 for x in compare_df['금액_SNC']])
        diff = kz_total - snc_total
        st.markdown(f"**🔢 KZ 금액 합계:** {kz_total:,.0f} (수동 입력 포함)")
        st.markdown(f"**🔢 SNC 금액 합계:** {snc_total:,.0f}")
        st.markdown(f"**➖ 차액 (KZ - SNC):** {diff:,.0f}")

        def highlight(row):
            style = [''] * len(row)
            if row['비고'] == '금액 불일치':
                style[2] = 'background-color: #ffd6d6'
                style[3] = 'background-color: #ffd6d6'
            elif row['비고'] == 'KZ 미승인':
                style[2] = 'background-color: #fff3cd'
            elif row['비고'] == 'SNC 미입력':
                style[3] = 'background-color: #d6eaff'
            return style

        st.subheader(f"비교 결과 (불일치 또는 누락 항목 총 {len(result_df)}건)")
        st.dataframe(result_df.style.apply(highlight, axis=1), use_container_width=True)

        csv = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("엑셀로 다운로드", data=csv, file_name="MBL_비교_결과.csv", mime="text/csv")

    except Exception as e:
        st.error(f"🚨 처리 중 오류가 발생했습니다: {str(e)}")
