import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cli.newspiko_cli import NewspikoCLI

class TestCLIFlow(unittest.TestCase):
    def setUp(self):
        self.cli = NewspikoCLI()

    @patch('src.crawler.NaverNewsCrawler.get_ranking_news')
    def test_list_news_naver(self, mock_get):
        mock_get.return_value = [{'press': '테스트언론', 'title': '테스트제목', 'link': 'http://test.com'}]
        self.cli.list_news("naver")
        self.assertEqual(len(self.cli.current_news_list), 1)
        self.assertEqual(self.cli.current_news_list[0]['title'], '테스트제목')

    @patch('src.crawler.NaverNewsCrawler.get_article_details')
    @patch('src.crawler.NaverNewsCrawler.get_comments')
    @patch('src.analyzer.NewsAnalyzer.analyze_opinion')
    def test_analyze_flow(self, mock_analyze, mock_comments, mock_details):
        mock_details.return_value = {'content': '본문내용', 'oid': '123', 'aid': '456'}
        mock_comments.return_value = [{'user': 'u1', 'text': 'c1', 'good': 0, 'bad': 0, 'time': ''}]
        mock_analyze.return_value = "AI 분석 결과 [SENTIMENT: pos=50, neg=50]"
        
        self.cli.current_news_list = [{'title': '제목', 'link': 'link'}]
        self.cli.analyze_news(0)
        
        mock_analyze.assert_called_once()
        mock_comments.assert_called_once()

if __name__ == "__main__":
    unittest.main()
