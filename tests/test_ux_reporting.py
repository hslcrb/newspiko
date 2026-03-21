import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# src 폴더 경로 추가
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'src'))

from src.analyzer import NewsAnalyzer
from src.main import AnalysisThread

def test_analyzer_status_callback():
    """NewsAnalyzer가 상태 변경 시 콜백을 호출하는지 확인"""
    analyzer = NewsAnalyzer(api_key="fake_key")
    analyzer.client = MagicMock()
    
    # 1회차 실패(형식 오류), 2회차 성공 시뮬레이션
    mock_responses = [
        MagicMock(choices=[MagicMock(message=MagicMock(content="형식 없는 응답"))]),
        MagicMock(choices=[MagicMock(message=MagicMock(content="[KEYWORDS: [\"A\"]] [SENTIMENT: pos=100, neg=0, neu=0] [SUSPICION: 0]"))])
    ]
    analyzer.client.chat.completions.create.side_effect = mock_responses
    
    callback = MagicMock()
    result = analyzer.analyze_opinion({"title": "T", "content": "C"}, [{"text": "C1"}], max_retries=2, status_callback=callback)
    
    # 콜백이 최소 2번 이상 호출되어야 함 (시도 1, 재시도 안내, 시도 2 등)
    assert callback.call_count >= 2
    calls = [c[0][0] for c in callback.call_args_list]
    assert any("AI 분석 시도 중... (1/2)" in s for s in calls)
    assert any("재시도합니다" in s for s in calls)
    assert "[KEYWORDS:" in result

def test_analysis_thread_signals():
    """AnalysisThread가 중간 상태와 최종 로그를 정상 배출하는지 확인"""
    analyzer = MagicMock()
    analyzer.analyze_opinion.return_value = "[KEYWORDS: ['X']] [SENTIMENT: pos=50, neg=50, neu=0] [SUSPICION: 10]"
    analyzer.parse_results.return_value = {
        "keywords": ["X"], "sentiment": {"pos": 50, "neg": 50, "neu": 0}, "suspicion": 10
    }
    
    # analyzer 내부에서 콜백을 호출하도록 모킹
    def side_effect(article, comments, max_retries=3, status_callback=None):
        if status_callback:
            status_callback("테스트 시작")
            status_callback("테스트 중")
        return analyzer.analyze_opinion.return_value

    analyzer.analyze_opinion.side_effect = side_effect
    
    thread = AnalysisThread(analyzer, {"title": "T", "content": "C"}, [])
    
    status_logs = []
    thread.status_msg.connect(lambda msg: status_logs.append(msg))
    
    finished_data = {}
    thread.finished.connect(lambda data: finished_data.update(data))
    
    thread.run()
    
    assert "테스트 시작" in status_logs
    assert "테스트 중" in status_logs
    assert "logs" in finished_data
    assert len(finished_data["logs"]) >= 2
    assert finished_data["logs"] == status_logs

if __name__ == "__main__":
    pytest.main([__file__, "-s"])
