# pages/check.py
import streamlit as st
import json
import pandas as pd
import zipfile
import io

st.title("📱 인스타 언팔체크")

st.markdown("""
**기능 설명**

인스타그램에서 받은 ZIP 파일을 업로드하면, 내가 팔로우하지만 나를 팔로우하지 않는 사람을 찾아줍니다.

1. 인스타그램에서 데이터 다운로드
2. 받은 ZIP 파일을 바로 업로드
3. 결과 확인 및 다운로드
""")

uploaded_zip = st.file_uploader("인스타그램 ZIP 파일 업로드", type="zip")

def extract_usernames(data):
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and all("string_list_data" in item for item in v):
                return set(entry['string_list_data'][0]['value'] for entry in v)
    elif isinstance(data, list):
        return set(entry['string_list_data'][0]['value'] for entry in data)
    return set()

def find_json_file(zip_file, keyword):
    files = [f for f in zip_file.namelist() if keyword in f and f.endswith(".json")]
    # followers_1.json 보다 following.json이 우선되면 안 되므로 정확한 조건 지정
    if keyword == "followers":
        files = [f for f in files if "followers_1.json" in f]
    elif keyword == "following":
        files = [f for f in files if f.endswith("following.json")]
    return files[0] if files else None

if uploaded_zip:
    try:
        with zipfile.ZipFile(uploaded_zip) as z:
            st.markdown("#### 🔍 ZIP 파일 내부 목록")
            st.write(z.namelist())  # 내부 파일 확인용

            followers_file = find_json_file(z, "followers")
            following_file = find_json_file(z, "following")

            if not followers_file or not following_file:
                st.error("ZIP 파일에서 followers 또는 following JSON 파일을 찾을 수 없습니다.")
            else:
                with z.open(followers_file) as f:
                    followers_data = json.load(f)
                with z.open(following_file) as f:
                    following_data = json.load(f)

                follower_usernames = extract_usernames(followers_data)
                following_usernames = extract_usernames(following_data)

                not_following_back = sorted(list(following_usernames - follower_usernames))

                st.success(f"총 {len(not_following_back)}명이 나를 팔로우하지 않아요.")
                st.write(not_following_back)

                df = pd.DataFrame(not_following_back, columns=["Not Following Back"])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("CSV로 다운로드", data=csv, file_name="not_following_back.csv", mime="text/csv")
    except Exception as e:
        st.error(f"처리 중 오류 발생: {e}")
