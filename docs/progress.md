# Progress

- 완료: PDF 최소 기능 전체, 인증·상품·검색, 송금·불변 원장·PostgreSQL 동시성, 신고·제재·감사, 전체·1대1 채팅·Redis 통합, 로그인/WebSocket 보안, README 실행 절차, CI/Dependabot/E2E 구성, 의존성·Git 이력 비밀 검사
- 현재 작업: 작업 4(보고서 제외) 로컬 검증 후 public 전환·push·Actions 확인
- 남음: GitHub Actions 실제 통과와 화면 아티팩트 확인; 별도 요청 시 최종 보고서·PDF 시각 검증·제출 파일명
- 최근 테스트: 전체 `57 passed, 2 skipped`; Redis 별도 `1 passed`; PostgreSQL 동시성 별도 `1 passed`; 관리자 대시보드 관련 `7 passed`; migration/Ruff/format/Bandit/pip-audit/deploy/Compose/비밀 이력 검사 통과
- 결정: GitHub Actions에서 PostgreSQL·Redis 외부 테스트와 Playwright 핵심 흐름 및 화면 증빙 실행, Dependabot 주간 점검
- 알려진 문제: Docker Desktop 엔진은 로컬에서 기동 정지(Compose 구문은 통과); 로컬 브라우저 런타임 오류로 실제 E2E는 Actions에서 검증; 운영 SECRET_KEY 필요
- 다음 명령: 전체 로컬 회귀·정적 검사 → 커밋 → public 전환·push → `gh run watch`와 E2E 아티팩트 확인
