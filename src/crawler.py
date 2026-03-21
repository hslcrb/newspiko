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

    def get_comments(self, oid, aid, page=None, pageSize=100, max_comments=None):
        """댓글 수집 (페이징 지원). page가 None이면 max_comments까지 전체 수집"""
        if not oid or not aid: return []
        
        headers = self.headers.copy()
        headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f"https://n.news.naver.com/article/comment/{oid}/{aid}"
        })
        
        # 1. 파라미터 감지
        url = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"
        pref_object_ids = [f"news{oid},{aid}", f"news{oid}{aid}"]
        
        found_params = {"ticket": "news", "pool": "cbox5", "objectId": pref_object_ids[0]}
        for obj_id in pref_object_ids:
            params = {"ticket": "news", "templateId": "default", "pool": "cbox5", "objectId": obj_id, "pageSize": 1, "page": 1}
            try:
                res = self.session.get(url, params=params, headers=headers, timeout=5)
                if 'success":true' in res.text:
                    found_params["objectId"] = obj_id
                    break
            except: continue

        def fetch_page(p_num):
            params = {
                "ticket": found_params["ticket"], "templateId": "default", 
                "pool": found_params["pool"], "objectId": found_params["objectId"],
                "lang": "ko", "country": "KR", "pageSize": pageSize, "page": p_num, "sort": "FAVORITE"
            }
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=10)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if not match: return []
                data = json.loads(match.group(0))
                comment_list = data.get('result', {}).get('commentList', [])
                
                results = []
                for c in comment_list:
                    results.append({
                        'no': c.get('commentNo'),
                        'user': c.get('userName', '익명'),
                        'text': c.get('contents', ''),
                        'good': c.get('sympathyCount', 0),
                        'bad': c.get('antisympathyCount', 0),
                        'time': c.get('regTime', '')
                    })
                return results
            except: return []

        if page is not None:
            return fetch_page(page)
        
        # 이전 방식 호환 (전체 수집)
        all_comments = []
        p = 1
        limit = max_comments or 500
        while len(all_comments) < limit:
            batch = fetch_page(p)
            if not batch: break
            all_comments.extend(batch)
            if len(batch) < pageSize: break
            p += 1
            time.sleep(0.1)
        return all_comments[:limit]
