import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def analyze_naver(url):
    print(f"Analyzing Naver: {url}")
    res = requests.get(url, headers=headers)
    html = res.text
    
    # 1. oid, aid 찾기
    oid = re.search(r'oid=(\d+)', url) or re.search(r'article/(\d+)/', url)
    aid = re.search(r'aid=(\d+)', url) or re.search(r'article/\d+/(\d+)', url)
    print(f"OID: {oid.group(1) if oid else 'N/A'}, AID: {aid.group(1) if aid else 'N/A'}")
    
    # 2. 모든 ticket, pool, objectId 패턴 추출
    tickets = re.findall(r'\"ticket\"\s*:\s*\"([^\"]+)\"', html)
    pools = re.findall(r'\"pool\"\s*:\s*\"([^\"]+)\"', html)
    template_ids = re.findall(r'\"templateId\"\s*:\s*\"([^\"]+)\"', html)
    object_ids = re.findall(r'\"objectId\"\s*:\s*\"([^\"]+)\"', html)
    
    print(f"All Tickets found: {list(set(tickets))}")
    print(f"All Pools found: {list(set(pools))}")
    print(f"All TemplateIds found: {list(set(template_ids))}")
    print(f"All ObjectIds found: {list(set(object_ids))}")
    
    # 3. 댓글 개수 확인 (u_cbox_count 등)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    count = soup.select_one('.u_cbox_count') or soup.select_one('.count')
    print(f"Comment Count in HTML: {count.text if count else 'Not Found'}")
    
    # script 내부의 g_news 등 검색
    if "g_news" in html: print("Found 'g_news' in HTML")
    if "commentList" in html: print("Found 'commentList' in HTML")

def analyze_daum(url):
    print(f"\nAnalyzing Daum: {url}")
    res = requests.get(url, headers=headers)
    html = res.text
    
    # Alex 설정 찾기
    post_id = re.search(r'\"postId\"\s*:\s*\"(\d+)\"', html) or \
              re.search(r'data-post-id=\"(\d+)\"', html) or \
              re.search(r'/v/(\d+)', url)
    print(f"Post ID: {post_id.group(1) if post_id else 'N/A'}")
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    count = soup.select_one('.alex-count-area') or soup.select_one('.num_txt')
    print(f"Comment Count in HTML: {count.text if count else 'Not Found'}")

if __name__ == "__main__":
    analyze_naver("https://n.news.naver.com/article/025/0003510578")
    analyze_daum("https://v.daum.net/v/20260321225027343")
