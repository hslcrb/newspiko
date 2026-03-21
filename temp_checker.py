import requests
import re
import json

headers = {'User-Agent': 'Mozilla/5.0'}

def check_naver(url):
    print(f"\n--- Checking Naver: {url} ---")
    r = requests.get(url, headers=headers)
    # objectId 찾기
    oid_match = re.search(r'\"objectId\":\"(.*?)\"', r.text)
    if oid_match:
        print(f"Found objectId: {oid_match.group(1)}")
    else:
        # 다른 형식 시도
        oid_match = re.search(r'objectId:\"(.*?)\"', r.text)
        if oid_match:
            print(f"Found objectId (alt): {oid_match.group(1)}")
        else:
            print("No objectId found in HTML")

def check_daum(url):
    print(f"\n--- Checking Daum: {url} ---")
    r = requests.get(url, headers=headers)
    # postId 찾기
    pid_match = re.search(r'\"postId\":\"(.*?)\"', r.text)
    if pid_match:
        print(f"Found postId: {pid_match.group(1)}")
    else:
        # data-post-id 찾기
        pid_match = re.search(r'data-post-id=\"(.*?)\"', r.text)
        if pid_match:
            print(f"Found data-post-id: {pid_match.group(1)}")
        else:
            print("No postId/articleId found in HTML")

if __name__ == "__main__":
    check_naver("https://n.news.naver.com/article/437/0000483987")
    check_daum("https://v.daum.net/v/20260321214325415")
