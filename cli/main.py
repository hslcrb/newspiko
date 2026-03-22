import sys
import os

# Newspiko CLI Entry Point
def run():
    # 프로젝트 루트 경로 추가 (cli 폴더의 상위 폴더)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    
    # NewspikoCLI 의 main 함수 실행
    try:
        from cli.newspiko_cli import main
        main()
    except Exception as e:
        print(f"CLI 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    run()
