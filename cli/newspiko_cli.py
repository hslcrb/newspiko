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
        self.analyzer = NewsAnalyzer(
            api_key=self.config_mgr.get("groq_api_key"),
            model=self.config_mgr.get("model")
        )
        self.detector = PatternDetector()
        self.current_news_list = []
        self.current_source = "naver"
        self.analysis_history = []  # 트렌드 분석용 히스토리 추가
        self.auto_analyze = False   # 자동 분석 모드
        self.last_analysis_text = "" # 마지막 분석 결과 저장용

    def print_help(self):
        print(f"\n{Fore.CYAN}=== Newspiko CLI 명령어 안내 ===")
        print(f"{Fore.WHITE}/naver             - 네이버 뉴스 랭킹 로드")
        print(f"{Fore.WHITE}/daum              - 다음 뉴스 랭킹 로드")
        print(f"{Fore.WHITE}/analyze <번호>    - 해당 번호 뉴스 AI 분석")
        print(f"{Fore.WHITE}/trend             - 현재 세션 분석 트렌드 요약")
        print(f"{Fore.WHITE}/save <파일명>      - 마지막 분석 결과를 텍스트 파일로 저장")
        print(f"{Fore.WHITE}/auto              - 자동 분석 모드 토글 (선택 시 즉시 분석)")
        print(f"{Fore.WHITE}/export <번호> <명> - 댓글 데이터를 CSV로 내보내기")
        print(f"{Fore.WHITE}/model <name>      - 분석 모델 변경")
        print(f"{Fore.WHITE}/api <key>         - API 키 저장")
        print(f"{Fore.WHITE}/help              - 도움말")
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
            comments = crawler.get_comments(news['link'])

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
        self.last_analysis_text = analysis
        parsing_res = self.analyzer.parse_results(analysis)
        
        print(f"\n{Fore.WHITE}{analysis}")
        
        print(f"\n{Fore.YELLOW}📋 [구조 분석 요약]")
        print(f"- 주요 키워드: {', '.join(parsing_res['keywords'][:5])}")
        print(f"- AI 진단 지수: {parsing_res['suspicion']}/100")
        s = parsing_res['sentiment']
        print(f"- 감성 분포:")
        print(f"  {Fore.GREEN}[긍정: {s['pos']}%]{Style.RESET_ALL} | {Fore.WHITE}[관망: {s['neu']}%]{Style.RESET_ALL} | {Fore.RED}[부정: {s['neg']}%]{Style.RESET_ALL}")
        
        # 히스토리에 기록
        self.analysis_history.append({
            "title": news['title'],
            "sentiment": s,
            "suspicion": parsing_res['suspicion']
        })

    def save_report(self, filename):
        if not self.last_analysis_text:
            print(f"{Fore.RED}저장할 분석 결과가 없습니다. 먼저 분석을 진행하세요.")
            return

        if not filename.endswith(".txt"): filename += ".txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.last_analysis_text)
            print(f"{Fore.GREEN}>>> 리포트 저장 성공: {filename}")
        except Exception as e:
            print(f"{Fore.RED}파일 저장 중 오류: {e}")

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
            comments = crawler.get_comments(news['link'])

        if not comments:
            print(f"{Fore.RED}내보낼 댓글이 없습니다.")
            return

        import pandas as pd
        df = pd.DataFrame(comments)
        if not filename.endswith(".csv"): filename += ".csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"{Fore.GREEN}>>> 성공적으로 저장되었습니다: {filename}")

    def show_trend(self):
        if not self.analysis_history:
            print(f"{Fore.RED}아직 분석된 데이터가 없습니다.")
            return
        
        print(f"\n{Fore.CYAN}=== [현재 세션 분석 트렌드 요약] ===")
        for i, entry in enumerate(self.analysis_history, 1):
            s = entry['sentiment']
            # 감성 우세 판단
            pos = s['pos']
            neg = s['neg']
            lean = f"{Fore.GREEN}긍정({pos}%)" if pos > neg else f"{Fore.RED}부정({neg}%)" if neg > pos else f"{Fore.WHITE}중립"
            
            print(f"{i:2}. {entry['title'][:30]}...")
            print(f"    - 성향: {lean} {Style.RESET_ALL}| 의심 지수: {entry['suspicion']}")

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
            elif cmd == "/trend":
                cli.show_trend()
            elif cmd == "/model":
                if args:
                    cli.config_mgr.set("model", args[0])
                    cli.analyzer = NewsAnalyzer(
                        api_key=cli.config_mgr.get("groq_api_key"),
                        model=args[0]
                    )
                    print(f"{Fore.CYAN}분석 모델이 변경되었습니다: {args[0]}")
                else:
                    current_model = cli.config_mgr.get("model", "llama-3.3-70b-versatile")
                    print(f"{Fore.YELLOW}현재 모델: {current_model}")
            elif cmd == "/api":
                if args:
                    cli.config_mgr.set("groq_api_key", args[0])
                    cli.analyzer = NewsAnalyzer(
                        api_key=args[0],
                        model=cli.config_mgr.get("model")
                    )
                    print(f"{Fore.CYAN}API 키가 저장되었습니다.")
                else: print(f"{Fore.RED}키를 입력하세요. 예: /api gsk_...")
            elif cmd == "/save":
                if args: cli.save_report(args[0])
                else: print(f"{Fore.RED}파일명을 입력하세요. 예: /save my_report.txt")
            elif cmd == "/auto":
                cli.auto_analyze = not cli.auto_analyze
                status = f"{Fore.GREEN}ON" if cli.auto_analyze else f"{Fore.RED}OFF"
                print(f"{Fore.CYAN}자동 분석 모드: {status}")
            elif cmd.isdigit():
                # 숫자만 입력했을 때의 처리
                idx = int(cmd) - 1
                if cli.auto_analyze:
                    cli.analyze_news(idx)
                else:
                    # 자동 모드가 아닐 때는 단순 선택 (추후 확장 가능)
                    if 0 <= idx < len(cli.current_news_list):
                        n = cli.current_news_list[idx]
                        print(f"{Fore.YELLOW}[선택됨] {n['press']} - {n['title']}")
                        print(f"분석하려면 '/analyze {cmd}' 를 입력하거나 '/auto'를 켜세요.")
                    else:
                        print(f"{Fore.RED}잘못된 번호입니다.")
            else:
                print(f"{Fore.RED}알 수 없는 명령어입니다. /help를 확인하세요.")
        except Exception as e:
            print(f"{Fore.RED}오류 발생: {e}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
