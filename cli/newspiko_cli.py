import os
import sys
import argparse
from colorama import init, Fore, Style

# 윈도우 한글 출력 호환성 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

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
        self.current_news_list = []
        self.current_source = "naver"

    def print_help(self):
        print(f"\n{Fore.CYAN}=== Newspiko CLI 명령어 안내 ===")
        print(f"{Fore.WHITE}/naver             - 네이버 뉴스 랭킹 로드")
        print(f"{Fore.WHITE}/daum              - 다음 뉴스 랭킹 로드")
        print(f"{Fore.WHITE}/analyze <번호>    - 해당 번호 뉴스 AI 분석")
        print(f"{Fore.WHITE}/export <번호> <명> - 댓글 데이터를 CSV로 내보내기")
        print(f"{Fore.WHITE}/api <key>         - Groq API 키 저장")
        print(f"{Fore.WHITE}/help              - 도움말 출력")
        print(f"{Fore.WHITE}/quit              - 종료")

    def list_news(self, source="naver"):
        self.current_source = source
        crawler = self.naver_crawler if source == "naver" else self.daum_crawler
        print(f"\n{Fore.CYAN}[{source.upper()} 랭킹 뉴스 수집 중...]{Style.RESET_ALL}")
        self.current_news_list = crawler.get_ranking_news()
        
        if not self.current_news_list:
            print(f"{Fore.RED}뉴스를 불러오지 못했습니다.")
            return

        for i, news in enumerate(self.current_news_list[:20], 1):
            print(f"{Fore.YELLOW}{i:2}. {Fore.WHITE}[{news['press']}] {news['title']}")

    def analyze_news(self, idx):
        if not (0 <= idx < len(self.current_news_list)):
            print(f"{Fore.RED}잘못된 번호입니다. (1-20 사이 입력)")
            return

        news = self.current_news_list[idx]
        crawler = self.naver_crawler if self.current_source == "naver" else self.daum_crawler
        
        print(f"\n{Fore.GREEN}>>> [{news['title']}] 상세 정보 수집 중...")
        details = crawler.get_article_details(news['link'])
        
        print(f"{Fore.GREEN}>>> 댓글 수집 중...")
        if self.current_source == "naver":
            comments = crawler.get_comments(details['oid'], details['aid'])
        else:
            comments = crawler.get_comments(details.get('article_id'))

        print(f"{Fore.GREEN}>>> 패턴 탐색 중...")
        pattern_res = self.detector.analyze(comments)
        
        print(f"\n{Fore.MAGENTA}=== [여론조작 의심 진단] ===")
        print(f"- 중복 유저: {len(pattern_res['heavy_users'])}명")
        print(f"- 매크로 의심: {len(pattern_res['macro_comments'])}건")
        print(f"- 의심 지수: {Fore.RED if pattern_res['suspicion_score'] > 50 else Fore.GREEN}{pattern_res['suspicion_score']}/100")

        if not self.analyzer.api_key:
            print(f"\n{Fore.RED}API 키가 설정되지 않아 AI 분석을 중단합니다. (/api 명령어로 설정하세요)")
            return

        print(f"\n{Fore.CYAN}>>> AI 여론 분석 엔진 가동...")
        analysis = self.analyzer.analyze_opinion({'title': news['title'], 'content': details['content']}, comments)
        print(f"\n{Fore.WHITE}{analysis}")

    def export_csv(self, idx, filename):
        if not (0 <= idx < len(self.current_news_list)):
            print(f"{Fore.RED}잘못된 번호입니다.")
            return

        news = self.current_news_list[idx]
        crawler = self.naver_crawler if self.current_source == "naver" else self.daum_crawler
        print(f"{Fore.GREEN}>>> 데이터 수집 및 CSV 변환 중...")
        
        details = crawler.get_article_details(news['link'])
        if self.current_source == "naver":
            comments = crawler.get_comments(details['oid'], details['aid'])
        else:
            comments = crawler.get_comments(details.get('article_id'))

        if not comments:
            print(f"{Fore.RED}내보낼 댓글이 없습니다.")
            return

        import pandas as pd
        df = pd.DataFrame(comments)
        if not filename.endswith(".csv"): filename += ".csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"{Fore.GREEN}>>> 성공적으로 저장되었습니다: {filename}")

def main():
    cli = NewspikoCLI()
    print(f"{Fore.CYAN}Newspiko CLI v1.0 (GUI 동일 기능 지원)")
    cli.print_help()

    while True:
        try:
            cmd_line = input(f"\n{Fore.GREEN}Newspiko > {Style.RESET_ALL}").strip()
            if not cmd_line: continue
            
            parts = cmd_line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "/quit":
                break
            elif cmd == "/help":
                cli.print_help()
            elif cmd == "/naver":
                cli.list_news("naver")
            elif cmd == "/daum":
                cli.list_news("daum")
            elif cmd == "/analyze":
                if args:
                    cli.analyze_news(int(args[0]) - 1)
                else: print(f"{Fore.RED}번호를 입력하세요. 예: /analyze 1")
            elif cmd == "/export":
                if len(args) >= 2:
                    cli.export_csv(int(args[0]) - 1, args[1])
                else: print(f"{Fore.RED}사용법: /export <번호> <파일명>")
            elif cmd == "/api":
                if args:
                    cli.config_mgr.set("groq_api_key", args[0])
                    cli.analyzer = NewsAnalyzer(api_key=args[0])
                    print(f"{Fore.CYAN}API 키가 저장되었습니다.")
                else: print(f"{Fore.RED}키를 입력하세요. 예: /api gsk_...")
            else:
                print(f"{Fore.RED}알 수 없는 명령어입니다. /help를 확인하세요.")
        except Exception as e:
            print(f"{Fore.RED}오류 발생: {e}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
