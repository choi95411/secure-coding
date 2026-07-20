# Progress

- 완료: 환경/PDF 분석, 구성 승인, 프로젝트 기반, 인증·프로필, 상품 CRUD·검색, 17개 관련 테스트
- 현재 작업: 작업 2 송금·원장 구현 완료, 신고·관리자 준비
- 남음: 송금·원장, 신고·제재·감사, 관리자 통합, 채팅, E2E, CI/README 마감, 보고서
- 최근 테스트: wallets 10 passed, PostgreSQL 전용 동시성 1 skipped; 작업 1은 17 passed
- 결정: Django 모놀리스, Docker PostgreSQL/Redis, 내부 포인트, WebSocket 전체/1:1, 로컬+Actions, 기존 저장소 공개 전환
- 알려진 문제: Docker daemon/Compose 미가동; 운영 SECRET_KEY 필요; 로그인 Rate Limit 후속
- 다음 명령: `.venv/bin/pytest -q`; 이후 `moderation` 신고·제재·감사 구현
