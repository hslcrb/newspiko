# 📋 Newspiko 고도화 및 운영 체계 수립 계획 보고서

본 보고서는 현재 Newspiko 시스템의 한계점을 극복하고, 상용 수준의 안정성과 보안성을 확보하기 위한 단계별 로드맵을 제시합니다.

---

## 1. AI 분석 엔진 아키텍처 혁신 (Strict Guardrails)

현행 "텍스트 기반 지시" 방식에서 "구조적 무결성 보장" 방식으로 전환합니다.

### 2.1 프롬프트 엔지니어링 고도화
- **System Message 분리**: AI의 역할을 '출력 형식의 수호자'로 정의하여 잡담이나 서식 위반을 원천 차단합니다.
- **Few-shot Prompting**: 이상적인 출력 예시를 프롬프트에 제공하여 모델의 이해도를 극대화합니다.
- **온도 조절**: `temperature`를 `0.1`~`0.2`로 낮추어 결정론적인(Deterministic) 출력을 유도합니다.

### 2.2 결과물 유효성 검증 로직 도입
- **Schema-first Design**: 출력 결과가 정해진 JSON 규격이나 태그 형식을 만족하는지 Python 수준에서 검증합니다.
- **자동 재시도 (Auto-Retry)**: 파싱 오류 발생 시 AI에게 오류 내용을 전달하고 최대 3회까지 재발행을 요청합니다.
- **Pydantic 연동**: AI의 응답을 강력한 타입 시스템으로 정적 검증합니다.

---

## 2. 브랜치 운영 및 릴리즈 전략 (Branching Plan)

협업 및 안정적인 배포를 위해 **GitFlow** 기반의 체계를 도입합니다.

| 브랜치 이름 | 용도 | 설명 |
| :--- | :--- | :--- |
| [main](file:///d:/newspiko/cli/newspiko_cli.py#114-156) | **배포본** | 상용 환경에서 작동하는 검증된 최적의 코드 (v1.0.x) |
| `develop` | **통합 개발** | 다음 릴리즈를 위해 개발 중인 기능들이 모이는 핵심 브랜치 |
| `feature/*` | **기능 개발** | 각 기능별 독립 개발 (예: `feature/ai-retry`, `feature/daum-fix`) |
| `hotfix/*` | **긴급 수정** | 배포본에서 발견된 치명적 버그 수정 |
| `release/*` | **배포 준비** | `develop`에서 [main](file:///d:/newspiko/cli/newspiko_cli.py#114-156)으로 가기 전 최종 검증 단계 |

- **태깅 규칙**: `v1.1.0-alpha`, `v1.1.0-rc`, `v1.1.0-final` 등 의미론적 버전 관리(SemVer)를 따릅니다.

---

## 3. 보안 및 저장소 관리 (Security & Management)

### 3.1 저장소 프라이빗 전환 (gh CLI 활용)
핵심 로직 보호 및 API 키 유출 방지를 위해 저장소 가시성을 즉시 변경합니다.
- **실행 명령**: `gh repo edit --visibility private`

### 3.2 민감 정보 격리
- [.env](file:///d:/newspiko/.env) 및 [config.dat](file:///d:/newspiko/config.dat)의 엄격한 관리.
- `git-filter-repo`를 활용하여 과거 커밋 내역에 포함되었을지 모르는 민감 정보 완전 소거.

---

## 4. 상세 실행 단계 (Action Items)

### [Phase 1: 인프라 강화]
1. `gh` 명령어를 사용하여 저장소 **Private** 전환.
2. `develop` 브랜치 생성 및 기본 브랜치로 설정.

### [Phase 2: AI 엔진 고쳐쓰기]
1. [src/analyzer.py](file:///d:/newspiko/src/analyzer.py)에 `System Message` 레이어 추가.
2. 정규표현식 및 JSON 파서를 활용한 **데이터 추출 검증기** 구현.
3. `/analyze` 명령 시 비정상 결과에 대한 재처리 로직 탑재.

### [Phase 3: 품질 보증]
1. 주요 API 응답 사례별 유닛 테스트 케이스 20종 구축.
2. CLI 환경에서 대량(10개 이상) 기사 연속 분석 안정성 테스트.

---

## 5. 기대 효과 및 목표
- AI의 출력 오류(Hallucination)율 **1% 미만**으로 하향.
- 데이터 내보내기 및 시각화 파이프라인의 **100% 자동화**.
- 체계적인 브랜치 관리로 인한 코드 안정성 및 추적성 확보.

본 계획은 사용자 승인 즉시 **Phase 1**부터 실행에 착수하겠습니다.
