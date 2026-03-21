import PyInstaller.__main__
import os
import sys

def build():
    # 프로젝트 루트 경로 설정
    project_root = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_root, "src", "main.py")
    
    # PyInstaller 옵션 설정
    opts = [
        main_script,
        "--name=Newspiko",
        "--windowed", # 콘솔 창 숨기기
        "--onefile",  # 단일 파일로 병합
        "--clean",
        f"--workpath={os.path.join(project_root, 'build')}",
        f"--distpath={os.path.join(project_root, 'dist')}",
        f"--specpath={project_root}",
        "--add-data=src;src", # 소스 코드 포함 (상대 경로 처리를 위해)
    ]
    
    print("PyInstaller 빌드를 시작합니다...")
    PyInstaller.__main__.run(opts)
    print("빌드가 완료되었습니다. 'dist' 폴더를 확인하세요.")

if __name__ == "__main__":
    if "PyInstaller" not in sys.modules:
        import subprocess
        print("PyInstaller가 설치되어 있지 않습니다. 설치를 진행합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    build()
