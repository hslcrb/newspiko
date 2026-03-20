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

분석 지침:
1. **여론 요약**: 현재 댓글들의 전반적인 분위기와 주요 논점을 요약하십시오.
2. **반응 분석**: 긍정/부정/중립 비율을 추정하고 감성 상태를 분석하십시오.
3. **조작 의심 탐지**: 
   - 매크로 의심 (중복 문구), 조직적 유포 (특정 키워드 집중), 극단적 선동 여부를 확인하십시오.
   - 조작 의심 지수 (0~100%)를 산출하고 근거를 제시하십시오.
4. **최종 결론**: 해당 뉴스의 여론이 자연스러운지, 아니면 특정 세력에 의해 편향되었을 가능성이 있는지 판단하십시오.

형식: 마크다운(Markdown)을 사용하여 전문적으로 작성하십시오.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"분석 중 오류 발생: {str(e)}"
