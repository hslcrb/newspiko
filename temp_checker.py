import requests
import re
import json
import sys
import os

# src 폴더를 패키지로 인식하도록 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.crawler import NaverNewsCrawler

def scan_naver_ranking():
    crawler = NaverNewsCrawler()
    news_list = crawler.get_ranking_news()
    print(f"\nScanning top 10 Naver news for comments...")
    
    for i, news in enumerate(news_list[:10]):
        try:
            details = crawler.get_article_details(news['link'])
            oid, aid = details['oid'], details['aid']
            
            url = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"
            combos = [
                ("news", "cbox5", "default"),
                ("news", "g_news", "default")
            ]
            
            best_status = "N/A"
            best_total = 0
            
            for ticket, pool, tid in combos:
                params = {
                    "ticket": ticket, "templateId": tid, "pool": pool,
                    "lang": "ko", "country": "KR", "objectId": f"news{oid},{aid}",
                    "pageSize": 5, "page": 1
                }
                res = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0', 'Referer': news['link']})
                match = re.search(r'\{.*\}', res.text, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    status = data.get('result', {}).get('exposureConfig', {}).get('status', 'N/A')
                    total = data.get('result', {}).get('count', {}).get('total', 0)
                    if total > 0 or status == "COMMENT_ON":
                        best_status = status
                        best_total = total
                        break
                    best_status = status
            
            print(f"[{i+1}] {news['title'][:30]}... -> Status: {best_status}, Total: {best_total} ({oid}/{aid})")
        except Exception as e:
            print(f"[{i+1}] Error: {e}")

from src.crawler_daum import DaumNewsCrawler

def scan_daum_ranking():
    crawler = DaumNewsCrawler()
    news_list = crawler.get_ranking_news()
    print(f"\nScanning top 3 Daum news for ANY postId pattern...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': 'https://v.daum.net'
    }
    
    for i, news in enumerate(news_list[:3]):
        try:
            res_html = requests.get(news['link'], headers=headers)
            html = res_html.text
            
            # 루즈한 postId 패턴
            post_ids = re.findall(r'postId\s*[:=]\s*[\"\']?(\d+)[\"\']?', html, re.IGNORECASE)
            client_ids = re.findall(r'clientId\s*[:=]\s*[\"\']?([^\s\"\',}]+)[\"\']?', html, re.IGNORECASE)
            
            print(f"[{i+1}] Found PostIDs: {list(set(post_ids))}")
            print(f"[{i+1}] Found ClientIDs: {list(set(client_ids))}")
            
            article_id = re.search(r'/v/(\d+)', news['link']).group(1)
            target_id = post_ids[0] if post_ids else article_id
            
            url = f"https://comment.daum.net/apis/v1/posts/{target_id}/comments"
            res = requests.get(url, params={"limit": 5, "offset": 0}, headers=headers)
            print(f"[{i+1}] TargetID: {target_id}, Status: {res.status_code}, Count: {len(res.json()) if res.status_code == 200 else 'Err'}")

        except Exception as e:
            print(f"[{i+1}] Error: {e}")

if __name__ == "__main__":
    scan_naver_ranking()
    scan_daum_ranking()
