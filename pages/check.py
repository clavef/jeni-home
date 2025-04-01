# pages/check.py
import streamlit as st
import json
import pandas as pd

st.title("📱 인스타 언팔체크")

st.markdown("""
**기능 설명**

인스타그램에서 받은 JSON 파일을 업로드하면, 내가 팔로우하지만 나를 팔로우하지 않는 사람을 찾아줍니다.

1. `followers_1.json` 파일을 업로드 (팔로워 목록)
2. `following.json` 파일을 업로드 (팔로잉 목록)
3. 결과 확인 및 다운로드
""")

uploaded_followers = st.file_uploader("팔로워 JSON 업로드 (followers_1.json)", type="json")
uploaded_following = st.file_uploader("팔로잉 JSON 업로드 (following.json)", type="json")

if uploaded_followers and uploaded_following:
    followers_data = json.load(uploaded_followers)
    following_data = json.load(uploaded_following)

    try:
        follower_usernames = set([entry['string_list_data'][0]['value'] for entry in followers_data])
        following_usernames = set([entry['string_list_data'][0]['value'] for entry in following_data])

        not_following_back = sorted(list(following_usernames - follower_usernames))

        st.success(f"총 {len(not_following_back)}명이 나를 팔로우하지 않아요.")
        st.write(not_following_back)

        df = pd.DataFrame(not_following_back, columns=["Not Following Back"])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("CSV로 다운로드", data=csv, file_name="not_following_back.csv", mime="text/csv")
    except Exception as e:
        st.error(f"처리 중 오류 발생: {e}")
