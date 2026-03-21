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

    def get_comments(self, oid, aid, max_comments=100):
        # 다음(Daum) 뉴스는 'Alex' 댓글 시스템을 사용합니다.
        # aid가 곧 post_id인 경우가 많으나, 정확하게는 페이지 소스에서 찾아야 합니다.
        # 여기서는 aid를 post_id로 가정하고 API를 호출합니다.
        
        url = f"https://comment.daum.net/apis/v1/posts/{aid}/comments"
        params = {
            "limit": min(max_comments, 100),
            "offset": 0,
            "order": "RECOMMEND" # BEST 순
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            comments = []
            for c in data:
                user_info = c.get('user', {})
                comments.append({
                    'user': user_info.get('displayName', '익명'),
                    'text': c.get('content', ''),
                    'good': c.get('likeCount', 0),
                    'bad': c.get('dislikeCount', 0),
                    'time': c.get('createdAt', '')[:10] # YYYY-MM-DD
                })
            return comments
        except Exception as e:
            print(f"Daum Crawler Error (Comments): {e}")
            return []
