# Newspiko AI 분석 작동 원리 (AI Principles)

Newspiko는 뉴스 본문과 댓글 데이터를 결합하여 여론의 흐름과 왜곡 가능성을 분석하는 지능형 엔진을 탑재하고 있습니다. 주요 작동 프로세스는 다음과 같습니다.

## 1. 데이터 수집 및 전처리 (Data Ingestion)
- **Crawler**: `NaverNewsCrawler` 및 `DaumNewsCrawler`가 최신 랭킹 뉴스의 본문과 실시간 댓글 데이터를 수집합니다.
- **Filtering**: 수집된 데이터는 `PatternDetector`를 통해 1차적으로 중복 작성자 및 매크로 의심 패턴(짧은 시간 내 대량 작성 등)을 필터링합니다.

## 2. 분석 컨텍스트 구성 (Context Construction)
- **NewsAnalyzer**: 수집된 기사 제목, 본문, 그리고 상위 댓글들을 하나의 정교한 프롬프트로 병합합니다.
- **Hybrid Context**: 기사 내용뿐만 아니라 댓글의 반응을 함께 제공함으로써, "기사가 독자에게 주는 영향"과 "댓글에 나타난 실제 반응"을 입체적으로 분석합니다.

## 3. LLM 추론 (LLM Inference)
- **Engine**: Groq API를 통해 **Llama-3.3-70b-versatile** (또는 사용자 설정 모델) 엔진을 사용합니다.
- **System Prompt**: AI 분석가는 다음과 같은 특정한 임무를 부여받습니다.
    - 뉴스 내부적/외부적 맥락 분석
    - 감성 분석 (긍정, 부정, 관망 비율 산출)
    - 주요 키워드 추출
    - 여론 왜곡 및 선동 의심 지수(Suspicion Score) 계산

## 4. 정형 데이터 추출 (Tag-based Parsing)
AI는 분석 결과를 사람이 읽기 쉬운 요약문과 함께, 시스템이 인식할 수 있는 전용 태그(`[KEYWORDS]`, `[SENTIMENT]`, `[SUSPICION]`)를 포함하여 응답합니다.
- **Regex Parsing**: `NewsAnalyzer.parse_results`가 정규 표현식을 사용하여 이 태그들로부터 수치 데이터를 추출합니다.
- **Visualization**: 추출된 데이터는 GUI의 감성 분석 바(Sentiment Bar)와 CLI의 트렌트 차트로 시각화됩니다.

## 5. 최종 리포트 출력
- 사용자에게는 태그가 제거된 깔끔한 분석 요약문이 제공되며, 정량적인 수치는 차트와 지수를 통해 직관적으로 표시됩니다.
