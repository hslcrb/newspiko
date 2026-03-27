import sys
import os

# src 폴더 경로 추가 (임포트 전 실행 필수)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path: sys.path.append(root_dir)
src_dir = os.path.join(root_dir, 'src')
if src_dir not in sys.path: sys.path.append(src_dir)

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
        # 유효한 태그를 포함해야 파싱 성공으로 간주되어 루프 종료됨
        analyzer.client.chat.completions.create.return_value.choices[0].message.content = "분석 완료 [KEYWORDS: [\"A\"]] [SENTIMENT: pos=100, neg=0, neu=0] [SUSPICION: 0]"
        
        result = analyzer.analyze_opinion(article, comments)
        assert "분석 완료" in result
        assert "[KEYWORDS:" in result
        
        # 호출 인자 확인 (System Message는 0번, User Message는 1번)
        args, kwargs = analyzer.client.chat.completions.create.call_args
        user_prompt = kwargs['messages'][1]['content']
        assert "제목" in user_prompt
        assert "댓글1" in user_prompt

def test_sentiment_parsing_in_main():
    from src.main import AnalysisThread 
    
    analyzer = MagicMock()
    analyzer.analyze_opinion.return_value = "결과 [SENTIMENT: pos=70, neg=20, neu=10]"
    # parse_results 모킹 필수
    analyzer.parse_results.return_value = {
        "sentiment": {"pos": 70, "neg": 20, "neu": 10},
        "keywords": ["A", "B"],
        "suspicion": 30
    }
    
    article = {"title": "T", "content": "C"}
    comments = []
    
    thread = AnalysisThread(analyzer, article, comments)
    
    # PyQt 시그널은 emit을 직접 패치할 수 없으므로 모킹된 슬롯을 연결하여 테스트
    mock_slot = MagicMock()
    thread.finished.connect(mock_slot)
    
    thread.run()
    
    assert mock_slot.called
    res_dict = mock_slot.call_args[0][0]
    assert res_dict["sentiment"]["pos"] == 70
    assert res_dict["sentiment"]["neg"] == 20
    assert res_dict["sentiment"]["neu"] == 10
    # 원문에서 태그가 제거되었는지 확인
    assert "[SENTIMENT:" not in res_dict["text"]

if __name__ == "__main__":
    pytest.main([__file__, "-s"])
