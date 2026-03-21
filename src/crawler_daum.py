import requests
from bs4 import BeautifulSoup
import json
import re
import time

class DaumNewsCrawler:
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
        urls = ["https://news.daum.net/ranking/popular", "https://news.daum.net/"]
        for url in urls:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200: continue
                soup = BeautifulSoup(response.content, 'html.parser')
                news_list = []
                items = soup.select('.list_ranking > li') or \
                        soup.select('.list_news2 > li') or \
                        soup.select('.item_ranking') or \
                        soup.select('.item_issue')
                
                if not news_list:
                    all_links = soup.find_all('a', href=re.compile(r'v\.daum\.net/v/\d+'))
                    for a in all_links:
                        title = a.get_text(strip=True)
                        if len(title) > 10:
                            news_list.append({
                                'press': "다음뉴스",
                                'title': title,
                                'link': a['href']
                            })
                if news_list: return news_list
            except Exception as e:
                print(f"Daum Crawler Trial Error ({url}): {e}")
        return []

    def get_article_details(self, url):
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            content_tag = soup.select_one('.article_view') or soup.select_one('#harmonyContainer') or soup.find('div', itemprop='articleBody')
            content = content_tag.get_text(strip=True) if content_tag else ""
            match = re.search(r'/v/(\d+)', url)
            article_id = match.group(1) if match else url.split('/')[-1]
            post_id = article_id
            pid_match = re.search(r'\"postId\"\s*:\s*\"(\d+)\"', response.text) or \
                        re.search(r'data-post-id=\"(\d+)\"', response.text)
            if pid_match: post_id = pid_match.group(1)
            return {'content': content, 'article_id': post_id}
        except Exception as e:
            print(f"Daum Crawler Error (Details): {e}")
            return {'content': "", 'article_id': ""}

    def get_comments(self, url, offset=0, limit=100, max_comments=None, sort_order='RECOMMEND'):
        """댓글 수집 (오프셋 지원). offset이 None이 아니면 단일 배치 반환"""
        if not url: return []
        try:
            res_html = self.session.get(url, headers=self.headers, timeout=10)
            html = res_html.text
            article_id_match = re.search(r'/v/(\d+)', url)
            article_id = article_id_match.group(1) if article_id_match else ""
            post_id_match = re.search(r'postId\s*[:=]\s*[\"\']?(\d+)[\"\']?', html, re.IGNORECASE)
            alex_post_id = post_id_match.group(1) if post_id_match else article_id
            if not alex_post_id: return []

            api_url = f"https://comment.daum.net/apis/v1/posts/{alex_post_id}/comments"
            headers = self.headers.copy()
            headers.update({'Referer': url, 'Origin': 'https://v.daum.net', 'Accept': 'application/json'})
            
            def fetch_batch(off):
                params = {"limit": limit, "offset": off, "order": "RECOMMEND" if sort_order == "RECOMMEND" else "LATEST"}
                res = self.session.get(api_url, params=params, headers=headers, timeout=10)
                if res.status_code != 200: return []
                data = res.json()
                results = []
                for c in data:
                    results.append({
                        'no': c.get('id'),
                        'user': c.get('user', {}).get('displayName', '익명'),
                        'text': c.get('content', ''),
                        'good': c.get('likeCount', 0),
                        'bad': c.get('dislikeCount', 0),
                        'time': c.get('createdAt', '')
                    })
                return results

            if offset is not None:
                return fetch_batch(offset)

            all_comments = []
            curr_off = 0
            limit_total = max_comments or 100
            while len(all_comments) < limit_total:
                batch = fetch_batch(curr_off)
                if not batch: break
                all_comments.extend(batch)
                if len(batch) < limit: break
                curr_off += limit
                time.sleep(0.05)
            return all_comments[:limit_total]
        except Exception as e:
            print(f"Daum 댓글 수집 오류: {e}")
            return []
