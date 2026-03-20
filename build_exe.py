import os
import subprocess
import sys

def build():
    print("Newspiko Build System starting...")
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 빌드 명령어 구성
    # --onefile: 단일 실행 파일
    # --windowed: 콘솔 창 없음
    # --name: 실행 파일 이름
    # --add-data: 추가 파일 포함 (config_manager 등에서 상대 경로 사용 시 주의)
    # 현재 구조(src/)를 고려하여 main.py를 엔트리 포인트로 설정
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "Newspiko",
        "--clean",
        "src/main.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    print("\nBuild complete! Check the 'dist' folder for Newspiko.exe")

if __name__ == "__main__":
    build()
