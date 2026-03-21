# GUI 상세 오류 안내 및 UX 개선 계획

AI 분석 중 발생하는 Rate Limit (429) 오류 및 재시도 상태를 터미널이 아닌 GUI 내에서 실시간으로 확인할 수 있도록 개선합니다.

## 제안된 변경 사항

### 1. AI 분석 엔진 ([src/analyzer.py](file:///d:/newspiko/src/analyzer.py))
- [analyze_opinion](file:///d:/newspiko/src/analyzer.py#16-66) 메서드에 `status_callback` 매개변수 추가.
- 재시도(Retry) 발생 및 에러(429 등) 발생 시 해당 콜백을 통해 상세 메시지 전달.
- [print](file:///d:/newspiko/cli/newspiko_cli.py#33-42) 문을 콜백 호출로 대체하여 GUI 가시성 확보.

### 2. GUI 연동 레이어 ([src/main.py](file:///d:/newspiko/src/main.py))
- [AnalysisThread](file:///d:/newspiko/src/main.py#14-39)에 `progress_updated` 시그널 추가.
- `analyzer.analyze_opinion` 호출 시 시그널을 방출하는 콜백 함수 전달.
- 메인 위젯에 상세 에러 정보를 표시할 `info_panel` 또는 확장된 에러 메시지 뷰 구현.

### 3. 스타일 시스템 ([src/styles.py](file:///d:/newspiko/src/styles.py))
- `--color-error` (빨간색) 토큰 추가하여 에러 메시지 가독성 증대.

## 검증 계획

### 수동 검증
1. 일부러 틀린 API 키를 입력하거나 짧은 시간에 반복 요청하여 429 오류 유도.
2. GUI 화면에서 "Attempt 1 failed: Rate limit reached..." 와 같은 메시지가 실시간으로 나타나는지 확인.
3. 재시도 성공 시 결과가 정상적으로 출력되는지 확인.
