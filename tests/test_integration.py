import pytest
import sys
import os

# src 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock
from src.crawler import NaverNewsCrawler
from src.analyzer import NewsAnalyzer
from src.config_manager import ConfigManager

def test_full_pipeline_mock():
    # 1. Config 로드
    cm = ConfigManager(config_path="test_pipeline.dat", key_path="test_pipeline.key")
    cm.set("groq_api_key", "fake_key")
    
    # 2. Crawler 모킹
    crawler = NaverNewsCrawler()
    mock_news = [{'press': 'A', 'title': 'T', 'link': 'L'}]
    mock_details = {'content': 'C', 'oid': '1', 'aid': '2'}
    mock_comments = [{'text': 'Comment1'}]
    
    with patch.object(crawler.session, 'get'), \
         patch.object(NaverNewsCrawler, 'get_ranking_news', return_value=mock_news), \
         patch.object(NaverNewsCrawler, 'get_article_details', return_value=mock_details), \
         patch.object(NaverNewsCrawler, 'get_comments', return_value=mock_comments), \
         patch('openai.OpenAI') as mock_openai:
             
        # Analyzer 모킹
        analyzer = NewsAnalyzer(api_key=cm.get("groq_api_key"))
        if not analyzer.api_key:
            analyzer.api_key = "fake_key"
        analyzer.client = mock_openai()
        analyzer.client.chat.completions.create.return_value.choices[0].message.content = """
[KEYWORDS: ["테스트", "통합", "성공"]]
[SENTIMENT: pos=50, neg=30, neu=20]
[SUSPICION: 30]
[SUMMARY]
통합 테스트 성공 리포트입니다.
"""
        
        # 3. 파이프라인 실행
        news = crawler.get_ranking_news()
        details = crawler.get_article_details(news[0]['link'])
        comments = crawler.get_comments(details['oid'], details['aid'])
        result = analyzer.analyze_opinion({'title': news[0]['title'], 'content': details['content']}, comments)
        
        assert "통합 테스트 성공 리포트" in result
        assert "[KEYWORDS" in result
        
    if os.path.exists("test_pipeline.dat"): os.remove("test_pipeline.dat")
    if os.path.exists("test_pipeline.key"): os.remove("test_pipeline.key")
