import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class NewsAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    def analyze_opinion(self, article, comments):
        if not self.client:
            return "Groq API 키가 설정되지 않았습니다. 설정에서 입력해 주세요."
        
        if not comments:
            return "분석할 댓글이 없습니다."

        # 대량 댓글 중 상위 100개 발췌 (토큰 제한 고려)
        comment_text = "\n".join([f"- {c['text']}" for c in comments[:100]])
        
        prompt = f"""
당신은 대한민국 뉴스 및 여론 분석 전문가입니다. 다음 뉴스 기사와 댓글들을 분석하여 여론의 반응과 여론조작 의심 여부를 보고하십시오.

[뉴스 제목]: {article['title']}
[본문 요약]: {article['content'][:500]}...

[수집된 댓글 목록]:
{comment_text}

분석 및 출력 지침 (반드시 다음 형식을 지키십시오):

1. **핵심 요약**: 해당 뉴스와 여론의 핵심을 3줄 이내로 요약하십시오.
2. **마인드맵 키워드**: 뉴스의 주요 갈등 요소와 키워드를 JSON 배열 형식으로 추출하십시오. (예: ["키워드1", "키워드2", ...])
3. **감성 분석**: 긍정/부정/관망 비율을 백분율로 산출하십시오.
4. **여론조작 및 집단성 진단**: 
   - 매크로, 조직적 유포, 선동성 문구 등 구체적 증거를 기반으로 '조작 의심 지수(0~100%)'를 제시하십시오.
5. **전문가 통찰**: 해당 이슈의 향후 전개 방향 및 여론 변화 가능성을 서술하십시오.

형식: 마크다운(Markdown)을 사용하여 가독성 있게 작성하십시오. 키워드 부분은 `[KEYWORDS: ...]` 형태로 포함시키십시오.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=4096,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"분석 중 오류 발생: {str(e)}"
