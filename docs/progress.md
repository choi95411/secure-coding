# Progress

- 완료: 환경/PDF 분석, 구성 승인, 인증·프로필, 상품 CRUD·검색, 지갑·송금·불변 원장·PostgreSQL 동시성, 신고·제재·관리자 감사/조정, 전체·1대1 채팅, WebSocket/로그인 보안, 핵심 통합 흐름
- 현재 작업: 작업 3 코드·전체 회귀·실제 Redis 검증 완료; 브라우저 E2E 환경 복구 대기
- 남음: Playwright E2E, GitHub Actions, 의존성·Git 이력 비밀 검사, README 마감, 최종 보고서와 PDF 시각 검증, public 전환
- 최근 테스트: 전체 `56 passed, 2 skipped`; Redis 통합 별도 `1 passed`; PostgreSQL 동시성 별도 `1 passed`; migration/Ruff/format/Bandit/deploy check 통과
- 결정: Django 모놀리스, PostgreSQL/Redis, 내부 포인트, 세션 WebSocket 전체/1:1, DB 행 잠금 메시지 제한, 로컬+Actions, 기존 저장소 공개 전환
- 알려진 문제: Docker Desktop 엔진이 `starting`에서 멈춤(WSL Redis로 채팅 검증 완료); 브라우저 런타임 sandbox 초기화 실패; 운영 SECRET_KEY 필요
- 다음 명령: 브라우저 런타임 복구 후 Playwright 핵심 E2E; 이후 작업 4 CI·README·보고서
