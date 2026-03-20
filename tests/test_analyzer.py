import pytest
from unittest.mock import MagicMock, patch
from src.analyzer import NewsAnalyzer

def test_analyzer_no_key():
    with patch.dict('os.environ', {'GROQ_API_KEY': ''}):
        analyzer = NewsAnalyzer(api_key=None)
        article = {"title": "테스트", "content": "내용"}
        result = analyzer.analyze_opinion(article, [{"text": "댓글"}])
        assert "Groq API 키" in result

def test_analyzer_prompt_generation():
    analyzer = NewsAnalyzer(api_key="fake_key")
    article = {"title": "제목", "content": "내용"}
    comments = [{"text": "댓글1"}, {"text": "댓글2"}]
    
    with patch('groq.Groq') as mock_groq:
        analyzer.client = mock_groq()
        analyzer.client.chat.completions.create.return_value.choices[0].message.content = "분석 결과"
        
        result = analyzer.analyze_opinion(article, comments)
        assert result == "분석 결과"
        
        # 호출 인자 확인
        args, kwargs = analyzer.client.chat.completions.create.call_args
        prompt = kwargs['messages'][0]['content']
        assert "제목" in prompt
        assert "댓글1" in prompt
