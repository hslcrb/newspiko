import sys
import os
import time
import io

# Windows 콘솔 인코딩 이슈 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# src 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawler import NaverNewsCrawler
from src.analyzer import NewsAnalyzer

def test_batch_stability():
    print("=== [Batch Stability Test Started] ===")
    crawler = NaverNewsCrawler()
    analyzer = NewsAnalyzer()
    
    if not analyzer.api_key:
        print("[!] GROQ_API_KEY not set. Skipping.")
        return

    print("1. Fetching news list...")
    news_list = crawler.get_ranking_news()
    
    # 상위 5개 기사 분석
    for i in range(min(5, len(news_list))):
        news = news_list[i]
        print(f"\n[{i+1}/5] Analyzing: {news['title']}")
        
        details = crawler.get_article_details(news['link'])
        # details에 title이 없을 경우를 대비해 병합
        article_data = {**news, **details}
        
        comments = crawler.get_comments(details['oid'], details['aid'], max_comments=30)
        
        start_time = time.time()
        analysis_text = analyzer.analyze_opinion(article_data, comments)
        parsing_res = analyzer.parse_results(analysis_text)
        duration = time.time() - start_time
        
        print(f"   - Analysis Duration: {duration:.2f}s")
        print(f"   - Keywords: {parsing_res['keywords']}")
        print(f"   - Sentiment: {parsing_res['sentiment']}")
        print(f"   - Suspicion: {parsing_res['suspicion']}")
        
        if not parsing_res['keywords'] or sum(parsing_res['sentiment'].values()) == 0:
            print("   [!] Warning: Parsing might have failed or tags missing.")
        else:
            print("   [OK] Analysis & Parsing Successful.")
        
        # API Rate Limit 고려 (필요 시)
        time.sleep(1)

    print("\n=== [Batch Stability Test Completed] ===")

if __name__ == "__main__":
    test_batch_stability()
