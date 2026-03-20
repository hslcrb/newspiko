import requests
from bs4 import BeautifulSoup
import re
import json
import time

class NaverNewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_ranking_news(self):
        url = "https://news.naver.com/main/ranking/popularDay.naver"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            ranking_boxes = soup.find_all('div', class_='rankingnews_box')
            
            for box in ranking_boxes:
                press_name = box.find('strong', class_='rankingnews_name').get_text(strip=True)
                items = box.find_all('li')
                for item in items:
                    title_tag = item.find('a', class_='list_title')
                    if title_tag:
                        news_list.append({
                            'press': press_name,
                            'title': title_tag.get_text(strip=True),
                            'link': title_tag['href']
                        })
            return news_list
        except Exception as e:
            print(f"Crawler Error (Ranking): {e}")
            return []

    def get_article_details(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출
            article_body = soup.select_one('#newsct_article') or soup.select_one('#dic_area') or soup.find('div', id='articleBodyContents')
            content = article_body.get_text(strip=True) if article_body else ""
            
            # ID 추출
            match = re.search(r'article/(\d+)/(\d+)', url)
            if not match:
                oid = re.search(r'oid=(\d+)', url)
                aid = re.search(r'aid=(\d+)', url)
                oid = oid.group(1) if oid else ""
                aid = aid.group(1) if aid else ""
            else:
                oid, aid = match.groups()

            return {
                'content': content,
                'oid': oid,
                'aid': aid
            }
        except Exception as e:
            print(f"Crawler Error (Details): {e}")
            return {'content': "", 'oid': "", 'aid': ""}

    def get_comments(self, oid, aid, count=30):
        if not oid or not aid: return []
        
        # 추천순(FAVORITE), 최신순(NEWLY) 등 다양한 정렬 시도 가능
        url = "https://apis.naver.com/comment/comment/get/v2/jsonp/commentList.json"
        params = {
            "ticket": "news",
            "templateId": "default", # 'default'가 가장 범용적
            "pool": "g_news",
            "lang": "ko",
            "country": "KR",
            "objectId": f"news{oid},{aid}",
            "pageSize": count,
            "page": 1,
            "sort": "FAVORITE"
        }
        
        headers = self.headers.copy()
        headers['Referer'] = f'https://n.news.naver.com/article/comment/{oid}/{aid}'
        
        try:
            # 여러 templateId 시도 (정치 섹션 등은 다를 수 있음)
            templates = ["default", "default_politics", "default_society"]
            for tid in templates:
                params["templateId"] = tid
                response = requests.get(url, params=params, headers=headers, timeout=10)
                json_text = re.sub(r'^[^\({]+\(', '', response.text)
                json_text = re.sub(r'\);?\s*$', '', json_text)
                data = json.loads(json_text)
                
                if 'result' in data and data['result'].get('commentList'):
                    comments = []
                    for c in data['result']['commentList']:
                        comments.append({
                            'user': c.get('userName', '익명'),
                            'text': c.get('contents', ''),
                            'good': c.get('sympathyCount', 0),
                            'bad': c.get('antisympathyCount', 0),
                            'time': c.get('regTime', '')
                        })
                    return comments
            return []
        except Exception as e:
            print(f"Crawler Error (Comments): {e}")
            return []
