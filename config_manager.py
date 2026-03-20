import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigManager:
    def __init__(self, config_path="config.dat", key_path=".secret.key"):
        self.config_path = config_path
        self.key_path = key_path
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
        self.config = self.load_config()

    def _load_or_create_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                return f.read()
        else:
            # 고유 키 생성 (실제 운영 시에는 시스템 UUID 등을 솔트로 사용할 수 있음)
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
            if os.name == 'nt': # Windows에서 파일 숨김 처리
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(self.key_path, 2)
            return key

    def load_config(self):
        import zlib
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        try:
            with open(self.config_path, "rb") as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                # 압축 해제
                decompressed_data = zlib.decompress(decrypted_data)
                return json.loads(decompressed_data.decode('utf-8'))
        except Exception:
            return self._create_default_config()

    def _create_default_config(self):
        default = {
            "groq_api_key": "",
            "theme": "dark",
            "last_section": 100
        }
        self.save_config(default)
        return default

    def save_config(self, config_dict=None):
        import zlib
        if config_dict:
            self.config = config_dict
        
        # 압축 후 암호화
        data = json.dumps(self.config).encode('utf-8')
        compressed_data = zlib.compress(data)
        encrypted_data = self.fernet.encrypt(compressed_data)
        with open(self.config_path, "wb") as f:
            f.write(encrypted_data)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

if __name__ == "__main__":
    # 테스트
    cm = ConfigManager()
    cm.set("groq_api_key", "gsk_test_12345")
    print("저장 완료")
    
    cm2 = ConfigManager()
    print(f"로드된 키: {cm2.get('groq_api_key')}")
