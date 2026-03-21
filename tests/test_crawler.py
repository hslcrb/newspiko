import pytest
import sys
import os

# src 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch
from src.crawler import NaverNewsCrawler

@pytest.fixture
def crawler():
    return NaverNewsCrawler()

def test_get_ranking_news_mock(crawler):
    mock_html = """
    <div class="rankingnews_box">
        <strong class="rankingnews_name">테스트언론</strong>
        <li><a class="list_title" href="https://test.com/1">테스트기사1</a></li>
    </div>
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = mock_html.encode('utf-8')
        
        news = crawler.get_ranking_news()
        assert len(news) == 1
        assert news[0]['press'] == "테스트언론"
        assert news[0]['title'] == "테스트기사1"

def test_article_details_parsing(crawler):
    mock_html = """
    <div id="newsct_article">본문 내용입니다.</div>
    """
    url = "https://n.news.naver.com/article/001/0000001"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = mock_html.encode('utf-8')
        
        details = crawler.get_article_details(url)
        assert details['content'] == "본문 내용입니다."
        assert details['oid'] == "001"
        assert details['aid'] == "0000001"
