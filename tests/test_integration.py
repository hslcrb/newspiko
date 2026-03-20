import pytest
from unittest.mock import patch
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
    
    with patch.object(NaverNewsCrawler, 'get_ranking_news', return_value=mock_news), \
         patch.object(NaverNewsCrawler, 'get_article_details', return_value=mock_details), \
         patch.object(NaverNewsCrawler, 'get_comments', return_value=mock_comments), \
         patch('groq.Groq') as mock_groq:
             
        # Analyzer 모킹
        analyzer = NewsAnalyzer(api_key=cm.get("groq_api_key"))
        analyzer.client = mock_groq()
        analyzer.client.chat.completions.create.return_value.choices[0].message.content = "Analysis Success"
        
        # 3. 파이프라인 실행
        news = crawler.get_ranking_news()
        details = crawler.get_article_details(news[0]['link'])
        comments = crawler.get_comments(details['oid'], details['aid'])
        result = analyzer.analyze_opinion({'title': news[0]['title'], 'content': details['content']}, comments)
        
        assert result == "Analysis Success"
        
    import os
    if os.path.exists("test_pipeline.dat"): os.remove("test_pipeline.dat")
    if os.path.exists("test_pipeline.key"): os.remove("test_pipeline.key")
