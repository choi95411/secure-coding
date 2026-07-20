# Progress

- 완료: PDF 최소 기능 전체, 인증·상품·검색, 송금·불변 원장·PostgreSQL 동시성, 신고·제재·감사, 전체·1대1 채팅·Redis 통합, 로그인/WebSocket 보안, README, public GitHub, CI/Dependabot/Playwright E2E, 화면 4장, 의존성·Git 이력 비밀 검사
- 현재 작업: 작업 4 중 보고서를 제외한 항목 완료; 최신 Actions v7 재검증
- 남음: 별도 요청 시 최종 보고서 원본·PDF, 분반·개인정보, PDF 시각 검증과 제출 파일명
- 최근 테스트: 로컬 전체 `57 passed, 2 skipped`; GitHub Actions PostgreSQL·Redis·Docker·Playwright 전체 통과; migration/Ruff/format/Bandit/pip-audit/deploy/Compose/비밀 이력 검사 통과
- 결정: public `choi95411/secure-coding`, GitHub Actions에서 외부 통합과 Playwright 핵심 흐름 및 화면 증빙 실행, Dependabot 주간 점검
- 알려진 문제: Docker Desktop 엔진은 로컬에서 기동 정지했으나 Compose·Docker build는 Actions에서 통과; 운영 배포와 최종 보고서는 범위 제외
- 다음 명령: `gh run list --repo choi95411/secure-coding`; 보고서 요청 시 개인정보를 받은 후 최종 보고서·PDF 생성