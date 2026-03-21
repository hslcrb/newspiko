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
            
            # Naver News Comment API (CBOX) 최신 규격 반영
            url = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"
            
            # 1. 최적의 파라미터 조합 탐색
            found_params = None
            
            # 모바일/데스크톱 크로스 헤더
            headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': f"https://n.news.naver.com/article/{oid}/{aid}"
            })

            # 시도할 조합 (ticket, pool, templateId)
            combos = [
                ("news", "cbox5", "default"),     # 최신 표준
                ("news", "g_news", "default"),    # 레거시 표준
                ("news", "cbox5", "m_news"),      # 모바일
                ("news", "g_news", "m_news")
            ]
            
            for ticket, pool, tid in combos:
                if found_params: break
                for obj_id in object_ids:
                    params = {
                        "ticket": ticket, "templateId": tid, "pool": pool,
                        "lang": "ko", "country": "KR", "objectId": obj_id,
                        "pageSize": 5, "page": 1
                    }
                    try:
                        response = self.session.get(url, params=params, headers=headers, timeout=5)
                        # JSONP 정밀 파싱: _callback(...) 또는 json(...) 형태 대응
                        match = re.search(r'\{.*\}', response.text, re.DOTALL)
                        if not match: continue
                        data = json.loads(match.group(0))
                        
                        if data.get('success'):
                            # API 호출 자체는 성공
                            found_params = {"ticket": ticket, "pool": pool, "templateId": tid, "objectId": obj_id}
                            if data.get('result', {}).get('count', {}).get('total', 0) > 0:
                                break # 실데이터 존재 시 확정
                    except: continue

            if not found_params:
                found_params = {"ticket": "news", "pool": "cbox5", "templateId": "default", "objectId": object_ids[0]}

            # 2. 실데이터 수집
            page = 1
            while len(all_comments) < max_comments:
                params = {
                    "ticket": found_params["ticket"], "templateId": found_params["templateId"], 
                    "pool": found_params["pool"], "objectId": found_params["objectId"],
                    "lang": "ko", "country": "KR", "pageSize": 100, "page": page, "sort": "FAVORITE"
                }
                try:
                    response = self.session.get(url, params=params, headers=headers, timeout=10)
                    match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if not match: break
                    data = json.loads(match.group(0))
                    
                    comment_list = data.get('result', {}).get('commentList', [])
                    if not comment_list: break
                    
                    for c in comment_list:
                        c_id = c.get('commentNo')
                        if any(existing.get('no') == c_id for existing in all_comments): continue
                        all_comments.append({
                            'no': c_id,
                            'user': c.get('userName', '익명'),
                            'text': c.get('contents', ''),
                            'good': c.get('sympathyCount', 0),
                            'bad': c.get('antisympathyCount', 0),
                            'time': c.get('regTime', '')
                        })
                    if len(comment_list) < 100: break
                    page += 1
                except: break
                time.sleep(0.05)
                
            return all_comments
        except Exception as e:
            print(f"Crawler Error (Comments): {e}")
            return all_comments
