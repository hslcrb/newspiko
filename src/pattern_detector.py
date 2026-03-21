from collections import Counter
import difflib

class PatternDetector:
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def analyze(self, comments):
        """
        댓글 목록을 분석하여 집단성 및 패턴을 탐지합니다.
        """
        if not comments:
            return {
                "heavy_users": [], 
                "user_counts": {},
                "macro_comments": [], 
                "similar_groups": [],
                "suspicion_score": 0
            }

        # 1. 중복 작성자 탐지 (Heavy Users)
        user_counts = Counter([c['user'] for c in comments])
        heavy_users = [user for user, count in user_counts.items() if count > 1]

        # 2. 매크로 의심 (동일 내용 반복)
        text_counts = Counter([c['text'].strip() for c in comments if len(c['text'].strip()) > 5])
        macro_comments = [text for text, count in text_counts.items() if count > 1]

        # 3. 유사 내용 집단성 탐지 (유사도 분석)
        # 내용이 80% 이상 유사한 댓글 쌍을 찾아 그룹화
        groups = []
        texts = [c['text'].strip() for c in comments if len(c['text'].strip()) > 10]
        
        # 단순화를 위해 상위 N개만 비교 (성능 고려)
        target_texts = texts[:50]
        for i in range(len(target_texts)):
            for j in range(i + 1, len(target_texts)):
                ratio = difflib.SequenceMatcher(None, target_texts[i], target_texts[j]).ratio()
                if ratio >= self.threshold:
                    groups.append((target_texts[i], target_texts[j], ratio))

        # 4. 시간대별 집중도 (Burst) - 생략 (현재 데이터에 초 단위 정밀도가 부족할 수 있음)
        # 대신 특정 키워드의 비정상적 빈도를 체크할 수도 있음

        return {
            "heavy_users": heavy_users,
            "user_counts": dict(user_counts),
            "macro_comments": macro_comments,
            "similar_groups": groups,
            "suspicion_score": self._calculate_score(heavy_users, macro_comments, groups)
        }

    def _calculate_score(self, heavy_users, macro_comments, groups):
        score = 0
        if heavy_users: score += len(heavy_users) * 10
        if macro_comments: score += len(macro_comments) * 20
        if groups: score += len(groups) * 15
        return min(score, 100)
