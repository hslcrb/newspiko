import unittest
import sys
import os

# src 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzer import NewsAnalyzer

class TestAnalyzerParsing(unittest.TestCase):
    def setUp(self):
        self.analyzer = NewsAnalyzer(api_key="test_key")

    def test_parse_results_success(self):
        sample_text = """
### 분석 보고서
요약: 테스트 뉴스입니다.
[KEYWORDS: ["애플", "아이폰", "출시"]]
[SENTIMENT: pos=70, neg=20, neu=10]
[SUSPICION: 15]
전문가 의견: 좋습니다.
"""
        results = self.analyzer.parse_results(sample_text)
        
        self.assertEqual(results["keywords"], ["애플", "아이폰", "출시"])
        self.assertEqual(results["sentiment"]["pos"], 70)
        self.assertEqual(results["sentiment"]["neg"], 20)
        self.assertEqual(results["sentiment"]["neu"], 10)
        self.assertEqual(results["suspicion"], 15)

    def test_parse_results_with_whitespace(self):
        sample_text = "[KEYWORDS:   [  \"공간\" , \"공백\"  ]  ]"
        results = self.analyzer.parse_results(sample_text)
        self.assertEqual(results["keywords"], ["공간", "공백"])

    def test_parse_results_missing_tags(self):
        sample_text = "서식이 전혀 없는 텍스트입니다."
        results = self.analyzer.parse_results(sample_text)
        
        self.assertEqual(results["keywords"], [])
        self.assertEqual(results["sentiment"]["pos"], 0)
        self.assertEqual(results["suspicion"], 0)

    def test_parse_results_malformed_json(self):
        sample_text = "[KEYWORDS: [이것은 JSON이 아님]]"
        results = self.analyzer.parse_results(sample_text)
        self.assertEqual(results["keywords"], [])

if __name__ == '__main__':
    unittest.main()
