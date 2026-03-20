import requests
from bs4 import BeautifulSoup
import json
import re

class DaumNewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_ranking_news(self):
        # 다음 뉴스 랭킹 (많이본 기사)
        url = "https://news.daum.net/ranking/popular"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            items = soup.select('.list_news2 > li')
            for item in items:
                title_tag = item.select_one('.link_txt')
                press_tag = item.select_one('.info_news')
                if title_tag:
                    news_list.append({
                        'press': press_tag.get_text(strip=True) if press_tag else "다음뉴스",
                        'title': title_tag.get_text(strip=True),
                        'link': title_tag['href']
                    })
            return news_list
        except Exception as e:
            print(f"Daum Crawler Error (Ranking): {e}")
            return []

    def get_article_details(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출
            content_tag = soup.select_one('.article_view')
            content = content_tag.get_text(strip=True) if content_tag else ""
            
            # 다음은 URL에서 ID 추출 (예: news.v.daum.net/v/2023...)
            article_id = url.split('/')[-1]
            
            return {
                'content': content,
                'oid': 'daum', # 다음은 통합 ID 사용 빈도가 높음
                'aid': article_id
            }
        except Exception as e:
            print(f"Daum Crawler Error (Details): {e}")
            return {'content': "", 'oid': "", 'aid': ""}

    def get_comments(self, oid, aid, max_comments=300):
        # 다음 댓글 (카카오 계정 연동 방식이므로 API 구조가 조금 다름)
        # 실제 운영 수준에서는 카카오 API 또는 웹 소스 분석 필요
        # 여기서는 프로토타입을 위해 상징적인 댓글 데이터 또는 가능한 수준의 수집 로직 모의
        # 다음의 댓글은 'comment-list' API를 사용함
        
        # 실제 구현은 복잡할 수 있으므로, 프로젝트 요구사항에 맞춰 Naver와 유사한 구조로 모킹하거나
        # 동작 가능한 공개 API가 있다면 연결 (여기서는 구조적 일관성을 위해 기본 틀 제공)
        return [
            {'user': '다음유저1', 'text': '다음 뉴스에서도 이 이슈가 뜨겁네요.', 'good': 10, 'bad': 2, 'time': '방금 전'},
            {'user': '다음유저2', 'text': '네이버와는 여론 분위기가 사뭇 다른 듯 합니다.', 'good': 5, 'bad': 1, 'time': '1분 전'}
        ]
