# [기획서] 여론 분석 시각화 고도화: 정치 성향 및 강도 세분화

뉴스 댓글의 여론을 단순 긍정/부정을 넘어, **정치적 성향(좌/우)**과 **의견의 강도(강경/온건)**를 한눈에 파악할 수 있도록 시각화 시스템을 전면 개편합니다.

## 주요 변경 사항

### 1. AI 분석 로직 고도화 ([analyzer.py](file:///d:/newspiko/src/analyzer.py))
- **분석 기준 변경**: 기존의 단순 감성 분석(Sentiment)을 정치적 성향 분석으로 전환합니다.
- **세부 분류**: 데이터를 4가지 카테고리로 분류하도록 AI 프롬프트를 수정합니다.
    - `Strong Left (강경 좌)`
    - `Moderate Left (온건 좌)`
    - `Moderate Right (온건 우)`
    - `Strong Right (강경 우)`
- **데이터 규격**: `[POLITICAL_SENTIMENT: sl=XX, ml=XX, mr=XX, sr=XX]` 형식의 새로운 태그를 도입합니다.

### 2. 시각화 UI 개선 ([main.py](file:///d:/newspiko/src/main.py), [styles.py](file:///d:/newspiko/src/styles.py))
- **4단계 그라데이션 바**: 단일 바 내부에 4가지 색상을 비율에 따라 배치합니다.
    - **강경 좌**: 진한 파랑 (`#1e40af`)
    - **온건 좌**: 연한 파랑 (`#60a5fa`)
    - **온건 우**: 연한 빨강 (`#f87171`)
    - **강경 우**: 진한 빨강 (`#b91c1c`)
- **범례 및 레이블 추가**: 그래프 상단 또는 하단에 "좌(Left)", "우(Right)" 문구와 각 색상이 의미하는 바를 명확히 표시합니다.
- **히스토리 차트 업데이트**: 하단의 트렌드 바 역시 4분할 색조를 반영하여 시간에 따른 성향 변화를 추적할 수 있게 합니다.

## 추진 계획 (Execution Plan)

1. **브랜치 작업**: `feature/political-sentiment-viz`에서 진행 (완료).
2. **엔진 수정**: [analyzer.py](file:///d:/newspiko/src/analyzer.py)의 시스템 메시지 및 파서 업데이트.
3. **UI 수정**: [main.py](file:///d:/newspiko/src/main.py)의 `pos_bar`, `neg_bar` 구조를 4분할 레이아웃으로 변경.
4. **스타일 정의**: [styles.py](file:///d:/newspiko/src/styles.py)에 정치 성향 전용 컬러 팰릿 추가.

## 사용자 확인 사항
> [!IMPORTANT]
> 이 기능은 댓글의 텍스트 맥락을 통해 정치적 스펙트럼을 추론하므로, 뉴스 주제에 따라 AI의 판단 기준이 주관적일 수 있습니다. '긍정/부정' 지표는 이제 '좌/우' 성향의 강도로 대체됩니다.

PR 및 머지는 요청하신 대로 최종 검토 후에만 진행하겠습니다. 확인 부탁드립니다.
