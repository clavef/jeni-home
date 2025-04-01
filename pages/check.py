# pages/check.py
import streamlit as st
import json
import pandas as pd
import zipfile
import io
import datetime

st.title("📱 인스타 언팔체크")

st.markdown("""
**기능 설명**

인스타그램에서 받은 ZIP 파일을 업로드하면, 내가 팔로우하지만 나를 팔로우하지 않는 사람을 찾아줍니다.

1. 인스타그램에서 데이터 다운로드
2. 받은 ZIP 파일을 바로 업로드
3. 결과 확인 및 다운로드
""")

uploaded_zip = st.file_uploader("인스타그램 ZIP 파일 업로드", type="zip")

def extract_following_info(data):
    results = []
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                for entry in v:
                    if "string_list_data" in entry:
                        string_data = entry["string_list_data"][0]
                        username = string_data.get("value")
                        timestamp = string_data.get("timestamp")
                        results.append({"username": username, "timestamp": timestamp})
    elif isinstance(data, list):
        for entry in data:
            if "string_list_data" in entry:
                string_data = entry["string_list_data"][0]
                username = string_data.get("value")
                timestamp = string_data.get("timestamp")
                results.append({"username": username, "timestamp": timestamp})
    return results

def format_time(ts):
    if not ts:
        return "-"
    dt = datetime.datetime.fromtimestamp(ts)
    delta_days = (datetime.datetime.now() - dt).days
    formatted = dt.strftime("%Y.%m.%d %H:%M")
    return f"{delta_days}일 전, {formatted}"

def find_json_file(zip_file, keyword):
    files = [f for f in zip_file.namelist() if keyword in f and f.endswith(".json")]
    if keyword == "followers":
        files = [f for f in files if "followers_1.json" in f]
    elif keyword == "following":
        files = [f for f in files if f.endswith("following.json")]
    return files[0] if files else None

if uploaded_zip:
    try:
        with zipfile.ZipFile(uploaded_zip) as z:
            followers_file = find_json_file(z, "followers")
            following_file = find_json_file(z, "following")

            if not followers_file or not following_file:
                st.error("ZIP 파일에서 followers 또는 following JSON 파일을 찾을 수 없습니다.")
            else:
                with z.open(followers_file) as f:
                    followers_data = json.load(f)
                with z.open(following_file) as f:
                    following_data = json.load(f)

                follower_usernames = set([entry["username"] for entry in extract_following_info(followers_data)])
                following_info = extract_following_info(following_data)

                results = []
                for entry in following_info:
                    username = entry["username"]
                    timestamp = entry["timestamp"]
                    if username not in follower_usernames:
                        results.append({
                            "ID": f"@[{username}](https://instagram.com/{username})",
                            "내가 팔로잉한 날짜": format_time(timestamp)
                        })

                st.success(f"총 {len(results)}명이 나를 팔로우하지 않아요.")
                st.dataframe(pd.DataFrame(results))

                df_export = pd.DataFrame(results)
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button("CSV로 다운로드", data=csv, file_name="not_following_back.csv", mime="text/csv")
    except Exception as e:
        st.error(f"처리 중 오류 발생: {e}")
