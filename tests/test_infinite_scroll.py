import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from crawler import NaverNewsCrawler
from crawler_daum import DaumNewsCrawler

@pytest.fixture
def naver_crawler():
    return NaverNewsCrawler()

@pytest.fixture
def daum_crawler():
    return DaumNewsCrawler()

def test_naver_pagination_logic(naver_crawler):
    """네이버 크롤러의 페이징(Page) 로직 검증"""
    with patch.object(naver_crawler.session, 'get') as mock_get:
        # 1. 파라미터 감지용 응답 (성공)
        mock_resp_detect = MagicMock()
        mock_resp_detect.text = '{"success":true}'
        
        # 2. 실제 데이터 응답 (100개)
        mock_resp_data = MagicMock()
        mock_resp_data.text = '_callback({"result":{"commentList":[{"commentNo": 1, "userName": "A", "contents": "Text1"}]}})'
        
        mock_get.side_effect = [mock_resp_detect, mock_resp_data]
        
        comments = naver_crawler.get_comments("123", "456", page=1)
        
        assert len(comments) == 1
        assert comments[0]['no'] == 1
        # pageSize 100, page 1 인자가 들어갔는지 확인
        args, kwargs = mock_get.call_args_list[1]
        assert kwargs['params']['page'] == 1
        assert kwargs['params']['pageSize'] == 100

def test_daum_pagination_logic(daum_crawler):
    """다음 크롤러의 페이징(Offset) 로직 검증"""
    with patch.object(daum_crawler.session, 'get') as mock_get:
        # 1. HTML ID 추출용 (postId 감지)
        mock_resp_html = MagicMock()
        mock_resp_html.text = 'postId: "789"'
        
        # 2. 실제 데이터 응답
        mock_resp_data = MagicMock()
        mock_resp_data.json.return_value = [{"id": 1, "user": {"displayName": "B"}, "content": "Text2"}]
        mock_resp_data.status_code = 200
        
        mock_get.side_effect = [mock_resp_html, mock_resp_data]
        
        comments = daum_crawler.get_comments("https://v.daum.net/v/123", offset=100)
        
        assert len(comments) == 1
        # offset 100 인자가 들어갔는지 확인
        args, kwargs = mock_get.call_args_list[1]
        assert kwargs['params']['offset'] == 100
        assert kwargs['params']['limit'] == 100

def test_infinite_scroll_state_management():
    """GUI 내 무한 스크롤 상태 전이 및 추가 로드 호출 로직 검증 (Logic only)"""
    from PyQt6.QtWidgets import QApplication
    from main import ModernNewsApp
    
    app = QApplication([])
    window = ModernNewsApp()
    
    # 초기 상태 확인
    assert window.comment_page == 1
    assert window.is_loading_more == False
    
    # 뉴스 선택 시 상태 리셋 확인
    window.news_list_widget.clear()
    window.current_news_list = [{'press':'A', 'title':'Title1', 'link':'https://n.news.naver.com/article/001/001'}]
    from PyQt6.QtWidgets import QListWidgetItem
    item = QListWidgetItem("Test Item")
    window.news_list_widget.addItem(item)
    
    with patch.object(window.crawler, 'get_comments', return_value=[]):
        with patch.object(window.crawler, 'get_article_details', return_value={'oid':'1', 'aid':'2', 'content':''}):
            window.comment_page = 5 # 임의로 변경
            window.on_news_selected(item)
            assert window.comment_page == 1
            assert window.current_comment_details['oid'] == '1'

    app.quit()
