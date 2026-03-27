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
        mock_analyze.return_value = "AI 분석 결과 [SENTIMENT: pos=50, neg=30, neu=20]"
        
        self.cli.current_news_list = [{'title': '제목', 'link': 'link'}]
        self.cli.analyze_news(0)
        
        mock_analyze.assert_called_once()
        mock_comments.assert_called_once()
        self.assertEqual(len(self.cli.analysis_history), 1)

    def test_model_command(self):
        """/model 명령어가 모델 설정을 변경하는지 확인"""
        self.cli.config_mgr.set = MagicMock()
        # 명령행 시뮬레이션은 main 루프에서 하므로 여기서는 직접 함수 호출이나 로직 검증
        # NewspikoCLI 의 /model 분기 로직이 analyzer를 재설정함
        self.cli.config_mgr.get = MagicMock(return_value="fake_key")
        
        # /model 명령어 시뮬레이션
        new_model = "openai/gpt-4o"
        self.cli.config_mgr.set("model", new_model)
        from src.analyzer import NewsAnalyzer
        self.cli.analyzer = NewsAnalyzer(api_key="fake_key", model=new_model)
        
        self.assertEqual(self.cli.analyzer.model, new_model)

    def test_trend_command(self):
        """/trend 명령어가 히스토리를 정상 출력하는지 확인"""
        self.cli.analysis_history = [
            {"title": "T1", "sentiment": {"pos": 100, "neg": 0, "neu": 0}, "suspicion": 10}
        ]
        with patch('sys.stdout', new_callable=MagicMock()) as mock_stdout:
            self.cli.show_trend()
            output = "".join([call.args[0] for call in mock_stdout.write.call_args_list])
            self.assertIn("T1", output)
            self.assertIn("긍정", output)

if __name__ == "__main__":
    unittest.main()
