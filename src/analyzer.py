import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class NewsAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        
        self.system_message = """당신은 대한민국 뉴스 및 여론 분석 전문가입니다. 
당신은 오직 분석 보고서만을 마크다운 형식으로 출력해야 하며, 서론이나 결론 등 잡담을 절대 섞지 마십시오.
모든 데이터는 댓글 원문을 기반으로 정성적/정량적 추론을 거쳐 산출해야 합니다.

반드시 다음 태그를 포함하여 데이터를 규격화하십시오 (파싱 엔진에서 사용됨):
1. 마인드맵: [KEYWORDS: ["키워드1", "키워드2", ...]]
2. 감성 점수: [SENTIMENT: pos=XX, neg=XX, neu=XX] (합계 100)
3. 진단 지수: [SUSPICION: XX] (0~100)"""

    def analyze_opinion(self, article, comments, max_retries=3, status_callback=None):
        """뉴스 내용과 댓글을 분석하여 여론 리포트를 생성합니다. (자동 재시도 및 상태 콜백 포함)"""
        if not self.client:
            return "Groq API 키가 설정되지 않았습니다. 설정에서 입력해 주세요."
        
        if not comments:
            return "분석할 댓글이 없습니다."

        # 상위 100개 댓글 발췌
        comment_text = "\n".join([f"- {c['text']}" for c in comments[:100]])
        
        user_prompt_base = f"""다음 뉴스 기사와 댓글들을 분석하여 보고서를 작성하십시오.

[뉴스 제목]: {article.get('title', '제목 없음')}
[본문 요약]: {article.get('content', '본문 없음')[:1000]}...

[수집된 댓글 목록]:
{comment_text}

분석 항목:
1. 핵심 요약 (3줄 이내)
2. 마인드맵 키워드 추출 (지정된 TAG 내 JSON 배열 형식)
3. 감성 분석 (긍정/부정/관망 비율 산출)
4. 여론조작 및 집단성 진단 (구체적 근거와 함께 SUSPICION 지수 제시)
5. 전문가 통찰 (향후 전개 방향 및 여론 변화 가능성)
"""
        
        last_error_feedback = ""
        
        for attempt in range(max_retries):
            try:
                user_message = user_prompt_base
                if last_error_feedback:
                    user_message += f"\n\n[이전 시도 오류 피드백]: {last_error_feedback}\n형식(TAG)을 반드시 엄수해서 다시 작성해줘."

                if status_callback:
                    status_callback(f"AI 분석 시도 중... ({attempt + 1}/{max_retries})")

                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": self.system_message},
                        {"role": "user", "content": user_message}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2,
                    max_tokens=4096,
                )
                
                analysis_result = chat_completion.choices[0].message.content
                
                # 결과 유효성 즉시 검증
                parsed = self.parse_results(analysis_result)
                
                # 필수 데이터 유무 확인
                if parsed["keywords"] and sum(parsed["sentiment"].values()) > 0:
                    return analysis_result
                else:
                    last_error_feedback = "필수 태그([KEYWORDS], [SENTIMENT], [SUSPICION]) 중 누락되었거나 형식이 잘못된 부분이 발견되었어."
                    msg = f"[AI-RETRY] 시도 {attempt+1} 결과가 규격에 맞지 않습니다. 재시도합니다."
                    if status_callback: status_callback(msg)
                    print(msg) # Keep print for console visibility if callback not set
                    
            except Exception as e:
                error_msg = f"API 호출 중 오류 발생: {str(e)}"
                last_error_feedback = error_msg
                msg = f"[AI-ERROR] 시도 {attempt+1} 실패: {error_msg}"
                if status_callback: status_callback(msg)
                print(msg) # Keep print for console visibility if callback not set
                
        return "AI 분석에 실패했습니다. (최대 재시도 횟수 초과 또는 API 오류)"

    def parse_results(self, text):
        """AI 응답 텍스트에서 구조화된 데이터를 추출합니다."""
        results = {
            "keywords": [],
            "sentiment": {"pos": 0, "neg": 0, "neu": 0},
            "suspicion": 0
        }
        
        try:
            # 1. 키워드 추출
            kw_match = re.search(r'\[KEYWORDS:\s*(\[.*?\])\s*\]', text, re.DOTALL | re.IGNORECASE)
            if kw_match:
                try:
                    results["keywords"] = json.loads(kw_match.group(1).strip())
                except json.JSONDecodeError:
                    raw_items = re.findall(r'"([^"]*)"', kw_match.group(1))
                    results["keywords"] = [item for item in raw_items if item.strip()]
                
            # 2. 감성 점수 추출
            sent_match = re.search(r'\[SENTIMENT:\s*pos=(\d+),\s*neg=(\d+),\s*neu=(\d+)\]', text, re.IGNORECASE)
            if sent_match:
                results["sentiment"] = {
                    "pos": int(sent_match.group(1)),
                    "neg": int(sent_match.group(2)),
                    "neu": int(sent_match.group(3))
                }
                
            # 3. 의심 지수 추출
            susp_match = re.search(r'\[SUSPICION:\s*(\d+)\]', text, re.IGNORECASE)
            if susp_match:
                results["suspicion"] = int(susp_match.group(1))
                
        except Exception as e:
            print(f"[AI-PARSER] Fatal Error: {e}")
            
        return results
