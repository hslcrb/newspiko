import requests
from bs4 import BeautifulSoup
import json
import re

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
        # 다음 뉴스 랭킹 (랭킹 페이지가 404일 경우 메인 페이지 활용)
        urls = ["https://news.daum.net/ranking/popular", "https://news.daum.net/"]
        
        for url in urls:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200: continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                news_list = []
                
                # 메인 페이지 및 랭킹 페이지 공통 셀렉터 시도
                items = soup.select('.list_ranking > li') or \
                        soup.select('.list_news2 > li') or \
                        soup.select('.item_ranking') or \
                        soup.select('.item_issue') # 메인 페이지 이슈 기사
                
                if not news_list:
                    # 최후의 수단: 페이지 내든 모든 v.daum.net 링크 추출
                    all_links = soup.find_all('a', href=re.compile(r'v\.daum\.net/v/\d+'))
                    for a in all_links:
                        title = a.get_text(strip=True)
                        if len(title) > 10: # 제목다운 것만
                            news_list.append({
                                'press': "다음뉴스",
                                'title': title,
                                'link': a['href']
                            })
                
                if news_list:
                    return news_list
            except Exception as e:
                print(f"Daum Crawler Trial Error ({url}): {e}")
                
        return []

    def get_article_details(self, url):
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출
            content_tag = soup.select_one('.article_view') or soup.select_one('#harmonyContainer') or soup.find('div', itemprop='articleBody')
            content = content_tag.get_text(strip=True) if content_tag else ""
            
            # 다음은 URL에서 ID 추출 (예: v.daum.net/v/2023...)
            match = re.search(r'/v/(\d+)', url)
            article_id = match.group(1) if match else url.split('/')[-1]
            
            # Alex용 PostID 추출 시도 (HTML 소스 내에서)
            post_id = article_id
            page_text = response.text
            # common patterns: "postId":"...", "post_id":"...", data-post-id="..."
            pid_match = re.search(r'\"postId\"\s*:\s*\"(\d+)\"', page_text) or \
                        re.search(r'data-post-id=\"(\d+)\"', page_text) or \
                        re.search(r'\"articleId\"\s*:\s*\"(\d+)\"', page_text)
            if pid_match:
                post_id = pid_match.group(1)
            
            return {
                'content': content,
                'article_id': post_id # 실제로 사용할 ID
            }
        except Exception as e:
            print(f"Daum Crawler Error (Details): {e}")
            return {'content': "", 'oid': "", 'aid': ""}

    def get_comments(self, url, max_comments=100, sort_order='RECOMMEND'):
        if not url: return []
        
        try:
            # 1. HTML에서 Alex postId 및 clientId 추출 시도
            res_html = self.session.get(url, headers=self.headers, timeout=10)
            html = res_html.text
            
            # 숫자형 article_id 추출
            article_id_match = re.search(r'/v/(\d+)', url)
            article_id = article_id_match.group(1) if article_id_match else ""
            
            # 루즈한 postId 및 clientId 패턴
            post_id_match = re.search(r'postId\s*[:=]\s*[\"\']?(\d+)[\"\']?', html, re.IGNORECASE)
            # data-post-id 또는 clientId 등도 후보가 될 수 있음
            
            alex_post_id = post_id_match.group(1) if post_id_match else article_id
            if not alex_post_id: return []

            # 2. 댓글 API 호출
            api_url = f"https://comment.daum.net/apis/v1/posts/{alex_post_id}/comments"
            
            headers = self.headers.copy()
            headers.update({
                'Referer': url,
                'Origin': 'https://v.daum.net',
                'Accept': 'application/json'
            })
            
            all_comments = []
            limit = 100
            offset = 0
            
            while len(all_comments) < max_comments:
                params = {
                    "limit": limit,
                    "offset": offset,
                    "order": "RECOMMEND" if sort_order == "RECOMMEND" else "LATEST"
                }
                response = self.session.get(api_url, params=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    break
                
                data = response.json()
                if not data:
                    break
                
                for c in data:
                    c_id = c.get('id')
                    user_info = c.get('user', {})
                    all_comments.append({
                        'no': c_id,
                        'user': user_info.get('displayName', '익명'),
                        'text': c.get('content', ''),
                        'good': c.get('likeCount', 0),
                        'bad': c.get('dislikeCount', 0),
                        'time': c.get('createdAt', '')
                    })
                
                if len(data) < limit:
                    break
                offset += limit
                time.sleep(0.05)
                
            return all_comments
        except Exception as e:
            print(f"Daum 댓글 수집 오류: {e}")
            return []
