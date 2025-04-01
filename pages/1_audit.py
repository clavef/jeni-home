import streamlit as st
import pandas as pd

def compare_amount_lists_fixed(kz_list, snc_list):
    if not isinstance(kz_list, list) or not isinstance(snc_list, list):
        return 'KZ 누락' if not isinstance(kz_list, list) else 'SNC 누락'
    if sorted(kz_list) == sorted(snc_list):
        return '일치'
    else:
        return '금액 불일치'

def highlight_discrepancies(row):
    style = [''] * 4
    if row['비고'] == '금액 불일치':
        style[1] = 'background-color: #ffd6d6'
        style[2] = 'background-color: #ffd6d6'
    elif row['비고'] == 'KZ 누락':
        style[1] = 'background-color: #fff3cd'
    elif row['비고'] == 'SNC 누락':
        style[2] = 'background-color: #d6eaff'
    return style

st.title("✅ SNC-KZ 정산 도우미")
st.write("KZ와 SNC의 엑셀 파일을 업로드하여 MBL별 금액 비교 결과를 확인하세요.")

file_kz = st.file_uploader("KZ 엑셀 파일 업로드 (.xlsx)", type=["xlsx"], key="kz")
file_snc = st.file_uploader("SNC 엑셀 파일 업로드 (.xlsx)", type=["xlsx"], key="snc")

if file_kz and file_snc:
    try:
        df_kz = pd.read_excel(file_kz)
        df_snc = pd.read_excel(file_snc)

        if not {'M.BL#', '승인금액'}.issubset(df_kz.columns):
            st.error("❌ KZ 파일에 'M.BL#' 또는 '승인금액' 열이 없습니다. 파일이 올바른지 확인해주세요.")
            st.stop()
        if not {'H.B/L NO', 'Unnamed: 11'}.issubset(df_snc.columns):
            st.error("❌ SNC 파일에 'H.B/L NO' 또는 'Unnamed: 11' 열이 없습니다. 파일이 올바른지 확인해주세요.")
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

        all_mbls = pd.Series(list(set(df_kz['MBL']).union(set(df_snc['MBL']))), name='MBL')

        kz_grouped = df_kz.groupby('MBL')['승인금액'].apply(lambda x: sorted(x.tolist())).reset_index()
        snc_grouped = df_snc.groupby('MBL')['금액_SNC'].apply(lambda x: sorted(x.tolist())).reset_index()

        compare_df = pd.merge(all_mbls.to_frame(), kz_grouped, on='MBL', how='left')
        compare_df = pd.merge(compare_df, snc_grouped, on='MBL', how='left')

        compare_df['비고'] = compare_df.apply(lambda row: compare_amount_lists_fixed(row['승인금액'], row['금액_SNC']), axis=1)

        result_df = compare_df[compare_df['비고'] != '일치'].sort_values(by='MBL')

        result_df.columns = ['MBL#', 'KZ금액', 'SNC금액', '비고']
        styled_df = result_df.style.apply(highlight_discrepancies, axis=1)

        st.subheader("비교 결과 (불일치 또는 누락 항목)")
        st.dataframe(styled_df, use_container_width=True)

        csv = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="엑셀로 다운로드",
            data=csv,
            file_name='MBL_비교_결과.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"🚨 처리 중 오류가 발생했습니다: {str(e)}")
