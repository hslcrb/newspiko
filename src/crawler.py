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
        self.session = self._create_session()

    def _create_session(self):
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get_ranking_news(self):
        url = "https://news.naver.com/main/ranking/popularDay.naver"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            ranking_boxes = soup.find_all('div', class_='rankingnews_box')
            
            for box in ranking_boxes:
                name_tag = box.find('strong', class_='rankingnews_name')
                if not name_tag: continue
                press_name = name_tag.get_text(strip=True)
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
            response = self.session.get(url, headers=self.headers, timeout=10)
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

    def get_comments(self, oid, aid, max_comments=500):
        if not oid or not aid: return []
        
        url = "https://apis.naver.com/comment/comment/get/v2/jsonp/commentList.json"
        
        # 시도해볼 ObjectID 형식들
        object_ids = [f"news{oid},{aid}", f"news{oid}{aid}"]
        
        headers = self.headers.copy()
        headers['Referer'] = f'https://n.news.naver.com/article/comment/{oid}/{aid}'
        
        all_comments = []
        try:
            templates = ["default", "default_politics", "default_society", "default_economy"]
            found_template = None
            found_object_id = None
            found_pool = "g_news"
            
            # 1. 적절한 템플릿 및 ObjectID 찾기
            for obj_id in object_ids:
                if found_template: break
                for tid in templates:
                    # 다양한 pool 후보 시도
                    for pool in ["g_news", "g_politics", "g_society", "g_economy"]:
                        params = {
                            "ticket": "news", "templateId": tid, "pool": pool,
                            "lang": "ko", "country": "KR", "objectId": obj_id,
                            "pageSize": 100, "page": 1, "sort": "FAVORITE"
                        }
                        response = self.session.get(url, params=params, headers=headers, timeout=10)
                        if response.status_code != 200: continue
                        
                        json_text = re.sub(r'^[^\({]+\(', '', response.text)
                        json_text = re.sub(r'\);?\s*$', '', json_text)
                        try:
                            data = json.loads(json_text)
                            if 'result' in data and data['result'].get('commentList'):
                                found_template = tid
                                found_object_id = obj_id
                                found_pool = pool
                                break
                        except:
                            continue
                    if found_template: break
            
            if not found_template:
                return []
            
            # 2. 페이징 처리하여 수집
            page = 1
            sort_types = ["FAVORITE", "NEWEST"]
            for sort in sort_types:
                if all_comments: break
                while len(all_comments) < max_comments:
                    params = {
                        "ticket": "news", "templateId": found_template, "pool": found_pool,
                        "lang": "ko", "country": "KR", "objectId": found_object_id,
                        "pageSize": 100, "page": page, "sort": sort
                    }
                    response = self.session.get(url, params=params, headers=headers, timeout=10)
                    if response.status_code != 200: break
                    
                    json_text = re.sub(r'^[^\({]+\(', '', response.text)
                    json_text = re.sub(r'\);?\s*$', '', json_text)
                    try:
                        data = json.loads(json_text)
                    except: break
                    
                    comment_list = data.get('result', {}).get('commentList', [])
                    if not comment_list: break
                    
                    for c in comment_list:
                        all_comments.append({
                            'user': c.get('userName', '익명'),
                            'text': c.get('contents', ''),
                            'good': c.get('sympathyCount', 0),
                            'bad': c.get('antisympathyCount', 0),
                            'time': c.get('regTime', '')
                        })
                    
                    if len(comment_list) < 100: break
                    page += 1
                    time.sleep(0.1)
                
            return all_comments
        except Exception as e:
            print(f"Crawler Error (Comments): {e}")
            return all_comments
