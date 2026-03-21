import sys
import os

# src 폴더를 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.crawler import NaverNewsCrawler
from src.crawler_daum import DaumNewsCrawler

def test_naver():
    print("\n=== [Naver Comment Test Start] ===")
    crawler = NaverNewsCrawler()
    
    print("1. Fetching ranking news...")
    news_list = crawler.get_ranking_news()
    if not news_list:
        print("[!] Failed to fetch news list.")
        return
    
    # 첫 번째 기사 선택
    article = news_list[0]
    print(f"2. Selected Article: {article['title']} ({article['press']})")
    
    print("3. Extracting article details...")
    details = crawler.get_article_details(article['link'])
    oid = details.get('oid')
    aid = details.get('aid')
    print(f"   - OID: {oid}, AID: {aid}")
    
    if not oid or not aid:
        print("[!] Failed to extract OID/AID.")
        return
        
    print("4. Fetching comments (max 30)...")
    comments = crawler.get_comments(oid, aid, max_comments=30)
    
    print(f"[OK] Result: Total {len(comments)} comments collected.")
    for i, c in enumerate(comments[:3]):
        print(f"   [{i+1}] {c['user']}: {c['text'][:50]}...")

def test_daum():
    print("\n=== [Daum Comment Test Start] ===")
    crawler = DaumNewsCrawler()
    
    print("1. Fetching ranking news...")
    news_list = crawler.get_ranking_news()
    if not news_list:
        print("[!] Failed to fetch news list.")
        return
    
    # 첫 번째 기사 선택
    article = news_list[0]
    print(f"2. Selected Article: {article['title']}")
    
    print("3. Extracting article details...")
    details = crawler.get_article_details(article['link'])
    article_id = details.get('article_id')
    print(f"   - Article ID: {article_id}")
    
    if not article_id:
        print("[!] Failed to extract Article ID.")
        return
        
    print("4. Fetching comments (max 30)...")
    comments = crawler.get_comments(article_id, max_comments=30)
    
    print(f"[OK] Result: Total {len(comments)} comments collected.")
    for i, c in enumerate(comments[:3]):
        print(f"   [{i+1}] {c['user']}: {c['text'][:50]}...")

if __name__ == "__main__":
    try:
        test_naver()
        test_daum()
    except Exception as e:
        print(f"\n[!] Error during test: {e}")
