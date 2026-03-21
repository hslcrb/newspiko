import re
import os

def check_file(filename, keywords):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        print(f"\n=== Checking {filename} ===")
        for kw in keywords:
            # "kw":"value" or kw:"value" or kw: "value"
            patterns = [
                rf'\"{kw}\"\s*:\s*\"(.*?)\"',
                rf'{kw}\s*:\s*\"(.*?)\"',
                rf'\"{kw}\"\s*:\s*([0-9]+)',
                rf'{kw}\s*:\s*([0-9]+)'
            ]
            found = False
            for p in patterns:
                matches = re.findall(p, content)
                if matches:
                    print(f"  Found {kw}: {matches[:5]}")
                    found = True
                    break
            if not found:
                print(f"  No {kw} found.")

if __name__ == "__main__":
    check_file('naver_sample.html', ['objectId', 'ticket', 'pool', 'templateId'])
    check_file('daum_sample.html', ['postId', 'articleId', 'clientKey', 'alex'])
