
import sys
import os

# src 디렉토리를 경로에 추가
sys.path.append(os.path.join(os.getcwd(), "src"))

from config_manager import ConfigManager

def update_model():
    # main.py에서 사용하는 경로와 동일하게 설정 (상위 디렉토리 기준)
    cm = ConfigManager(config_path="config.dat", key_path=".secret.key")
    cm.set("model", "openai/gpt-oss-120b")
    print(f"Model updated to: {cm.get('model')}")

if __name__ == "__main__":
    update_model()
