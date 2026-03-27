import os
import pytest
import sys

# src 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager

def test_config_encryption_decryption():
    config_path = "test_config.dat"
    key_path = "test_secret.key"
    
    # 초기화
    if os.path.exists(config_path): os.remove(config_path)
    if os.path.exists(key_path): os.remove(key_path)
    
    cm = ConfigManager(config_path=config_path, key_path=key_path)
    test_key = "gsk_test_api_key_123"
    cm.set("groq_api_key", test_key)
    
    # 새 인스턴스로 로드 확인
    cm2 = ConfigManager(config_path=config_path, key_path=key_path)
    assert cm2.get("groq_api_key") == test_key
    
    # 파일이 실제로 비텍스트(암호화/압축) 상태인지 확인
    with open(config_path, "rb") as f:
        content = f.read()
        assert b"groq_api_key" not in content # 평문으로 존재하면 안됨
        
    # 정리
    os.remove(config_path)
    os.remove(key_path)

def test_config_default_values():
    config_path = "test_config_def.dat"
    key_path = "test_secret_def.key"
    
    cm = ConfigManager(config_path=config_path, key_path=key_path)
    assert cm.get("theme") == "dark"
    assert cm.get("model") == "openai/gpt-oss-120b"
    assert cm.get("last_section") == 100
    
    os.remove(config_path)
    os.remove(key_path)
