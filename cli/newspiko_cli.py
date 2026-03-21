import os
import sys
import argparse
from colorama import init, Fore, Style

# src 폴더를 패키지로 인식하도록 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawler import NaverNewsCrawler
from src.crawler_daum import DaumNewsCrawler
from src.analyzer import NewsAnalyzer
from src.config_manager import ConfigManager
from src.pattern_detector import PatternDetector

init(autoreset=True)

class NewspikoCLI:
    def __init__(self):
        self.config_mgr = ConfigManager(config_path="config.dat", key_path=".secret.key")
        self.naver_crawler = NaverNewsCrawler()
        self.daum_crawler = DaumNewsCrawler()
        self.analyzer = NewsAnalyzer(api_key=self.config_mgr.get("groq_api_key"))
        self.detector = PatternDetector()

    def list_news(self, source="naver"):
        crawler = self.naver_crawler if source == "naver" else self.daum_crawler
        print(f"\n{Fore.CYAN}[{source.upper()} 랭킹 뉴스 수집 중...]{Style.RESET_ALL}")
        news_list = crawler.get_ranking_news()
        
        if not news_list:
            print(f"{Fore.RED}뉴스를 불러오지 못했습니다.")
            return []

        for i, news in enumerate(news_list[:20], 1):
            print(f"{Fore.YELLOW}{i:2}. {Fore.WHITE}[{news['press']}] {news['title']}")
        
        return news_list

    def analyze_news(self, news, source="naver"):
        crawler = self.naver_crawler if source == "naver" else self.daum_crawler
        
        print(f"\n{Fore.GREEN}>>> 기사 상세 정보 수집 중...")
        details = crawler.get_article_details(news['link'])
        
        print(f"{Fore.GREEN}>>> 댓글 수집 중...")
        # Daum과 Naver의 get_comments 인자가 다름 (Naver: oid, aid / Daum: article_id)
        if source == "naver":
            comments = crawler.get_comments(details['oid'], details['aid'])
        else:
            comments = crawler.get_comments(details.get('article_id'))

        print(f"{Fore.GREEN}>>> 패턴 탐색 중...")
        pattern_res = self.detector.analyze(comments)
        
        print(f"\n{Fore.MAGENTA}=== [패턴 분석 결과] ===")
        print(f"- 중복 유저: {len(pattern_res['heavy_users'])}명")
        print(f"- 매크로 의심: {len(pattern_res['macro_comments'])}건")
        print(f"- 의심 지수: {pattern_res['suspicion_score']}/100")

        if not self.analyzer.api_key:
            print(f"\n{Fore.RED}API 키가 설정되지 않아 AI 분석을 중단합니다.")
            return

        print(f"\n{Fore.CYAN}>>> AI 여론 분석 엔진 가동 (Groq Llama-3)...")
        analysis = self.analyzer.analyze_opinion({'title': news['title'], 'content': details['content']}, comments)
        
        print(f"\n{Fore.WHITE}{analysis}")

def main():
    parser = argparse.ArgumentParser(description="Newspiko CLI - 고성능 여론 분석 에이전트")
    parser.add_argument("--source", choices=["naver", "daum"], default="naver", help="뉴스 소스 선택 (기본: naver)")
    parser.add_argument("--limit", type=int, default=10, help="표시할 뉴스 개수")
    
    args = parser.parse_args()
    cli = NewspikoCLI()
    
    news_list = cli.list_news(args.source)
    if not news_list:
        return

    try:
        choice = input(f"\n분석할 기사 번호를 입력하세요 (1-{len(news_list[:20])}, q는 종료): ")
        if choice.lower() == 'q':
            return
            
        idx = int(choice) - 1
        if 0 <= idx < len(news_list):
            cli.analyze_news(news_list[idx], args.source)
        else:
            print(f"{Fore.RED}잘못된 번호입니다.")
    except ValueError:
        print(f"{Fore.RED}숫자를 입력해 주세요.")
    except KeyboardInterrupt:
        print("\n종료합니다.")

if __name__ == "__main__":
    main()
