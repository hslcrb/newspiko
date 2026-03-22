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
from unittest.mock import patch, MagicMock

def test_batch_stability():
    print("=== [Batch Stability Test Started] ===")
    crawler = NaverNewsCrawler()
    analyzer = NewsAnalyzer()
    
    if not analyzer.api_key:
        analyzer.api_key = "fake_key"

    print("1. Fetching news list...")
    news_list = crawler.get_ranking_news()
    
    # 상위 5개 기사 분석
    for i in range(min(5, len(news_list))):
        news = news_list[i]
        print(f"\n[{i+1}/5] Analyzing: {news['title']}")
        
        details = crawler.get_article_details(news['link'])
        article_data = {**news, **details}
        comments = crawler.get_comments(details['oid'], details['aid'], max_comments=30)
        
        start_time = time.time()
        # API 호출 모킹 (엄격한 정규식 규격 준수)
        with patch.object(analyzer, 'analyze_opinion') as mock_analyze:
            mock_analyze.return_value = """
[KEYWORDS: ["배치", "테스트", "성공"]]
[POLITICAL_SENTIMENT: sl=40, ml=40, mr=10, sr=10]
[SUSPICION: 10]
[SUMMARY]
배치 안정성 테스트 가상 리포트입니다.
"""
            analysis_text = analyzer.analyze_opinion(article_data, comments)
        
        # 실제 파싱 로직 테스트
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
        
        time.sleep(0.1)

    print("\n=== [Batch Stability Test Completed] ===")

if __name__ == "__main__":
    test_batch_stability()
