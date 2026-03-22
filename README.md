# 📰 Newspiko: AI 기반 뉴스 여론 분석 및 조작 탐지 시스템

> [!IMPORTANT]
> **🚧 현재 개발 중 (Under Development)**: 본 프로젝트는 현재 기능 고도화 및 안정화 단계에 있습니다. 일부 인터페이스나 API 규격이 변경될 수 있으니 참고하시기 바랍니다.

**Newspiko**는 포털 뉴스(네이버, 다음)의 댓글 데이터를 실시간으로 수집하고, 인공지능(Groq Llama 3)을 활용하여 여론의 흐름을 분석하며, 조직적인 여론 조작 의심 패턴을 탐지하는 상용 등급의 분석 도구입니다.

---

## ✨ 핵심 기능

### 1. 다중 플랫폼 뉴스 크롤링
- **Naver News**: 랭킹 뉴스 및 일반 기사의 댓글 실시간 수집 (`cbox5` 최신 인터페이스 대응)
- **Daum News**: `Alex` 댓글 시스템 보안 우회 및 동적 `postId` 추출을 통한 완벽한 데이터 수집

### 2. AI 여론 분석 엔진 (Groq 기반)
- **핵심 요약**: 수천 개의 댓글 중 주요 쟁점을 3줄로 요약
- **키워드 마인드맵**: 여론의 중심이 되는 키워드를 추출하여 시각화 데이터 제공
- **정치 성향 분석 (Spectrum Analysis)**: 좌(Blue)/우(Red) 성향과 강경/온건 4단계 정밀 데이터 산출

### 3. 여론 조작 및 매크로 탐지 (Pattern Detector)
- **중복 유저 추적**: 짧은 시간 내 다수의 댓글을 작성하는 헤비 유저 식별
- **매크로 패턴 분석**: 동일 문구 반복, 시간적 규칙성 등을 분석하여 '조작 의심 지수' 산출
- **집단성 진단**: 특정 세력에 의한 조직적 여론 유포 정황 포착

### 4. 하이브리드 인터페이스 (CLI & GUI)
- **GUI 모드**: PyQt 기반의 직관적인 사용자 인터페이스와 차트 시각화 제공
- **CLI 모드**: 터미널 기반의 REPL 환경 지원 (`/api`, `/naver`, `/analyze`, `/export` 등)
- **데이터 내보내기**: 분석된 댓글 데이터를 CSV 형식으로 저장 가능

---

## 🛠 설치 및 실행 방법

### 요구 사항
- Python 3.8+
- Groq API Key (AI 분석용)

### 설치 단계
1. 저장소 클론:
   ```bash
   git clone https://github.com/hslcrb/newspiko.git
   cd newspiko
   ```
2. 가상환경 구축 및 의존성 설치:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

### 실행 방법
- **GUI 실행**: `python src/main.py`
- **CLI 실행**: `python cli/main.py` (또는 `python cli/newspiko_cli.py`)

---

## ⌨️ CLI 명령어 안내
- `/naver`: 네이버 뉴스 랭킹 로드
- `/daum`: 다음 뉴스 랭킹 로드
- `/analyze <번호>`: 해당 번호 뉴스에 대한 AI 및 패턴 분석 수행
- `/trend`: 현재 세션 분석 데이터 트렌드 및 요약 보기
- `/export <번호> <파일명>`: 특정 뉴스의 댓글 데이터를 CSV로 저장
- `/model <name>`: 분석용 AI 모델 실시간 변경
- `/api <key>`: Groq API 키 설정 고정
- `/help`: 도움말 출력
- `/quit`: 프로그램 종료

---

## ⚖️ 라이선스 (License)
본 프로젝트는 **GNU General Public License v3.0 (GPL-3.0)**에 따라 배포됩니다. 상세 내용은 [LICENSE](./LICENSE) 파일을 참조하십시오.

---

## 🤝 기여하기
버그 보고, 기능 제안 및 Pull Request는 언제나 환영합니다!

---

**Copyright (c) Rheehose (Rhee Creative) 2008-2026**
