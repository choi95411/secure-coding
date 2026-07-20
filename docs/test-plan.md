# Test Plan

계층은 모델 제약, Form/서비스 단위, View·DB 통합, 인증·권한, 파일 업로드, WebSocket, PostgreSQL 트랜잭션·동시성, Playwright E2E다.

- 작업 1: 가입·중복·비밀번호 해시·차단 로그인·POST 로그아웃·마이페이지 인증·본인 프로필·XSS, 상품 CRUD·업로드 검증·소유권·소프트 삭제·공개 범위, 검색 필터·정렬·빈 값·SQLi 문자열·Reflected XSS.
- 작업 2: 지갑 초기 포인트, 양의 정수·자기 송금·비활성 수신자·잔액 초과, 멱등 재요청, 실패 롤백, 불변 원장, 관리자 조정 및 감사, PostgreSQL 별도 연결 동시 송금. 신고 중복·자동 제재·복구와 일반 사용자 관리자 접근 차단.
- 작업 3: 전체/1대1 대화 정규화, 비참여자 차단, 숨김 메시지, XSS escape, WebSocket 미인증·비참여자 거절, 메시지 길이·Rate Limit·영속화·브로드캐스트, 실제 ASGI 세션 쿠키 인증과 신뢰하지 않는 Origin 차단, 로그인 실패 잠금·성공 초기화·식별자 비식별화, 핵심 A/B 통합 흐름.

## 최근 결과

- SQLite 전체 회귀: `56 passed, 2 skipped` (2026-07-20).
- Ruff lint/format, migration drift, Bandit: 통과.
- PostgreSQL 송금 동시성: 실제 `postgres:17-alpine` 환경에서 `1 passed`.
- Redis 채널 계층 테스트: WSL Redis 8.0.5를 56379 포트에서 영속화 없이 격리 실행해 `1 passed`.
- Playwright 브라우저 E2E: 핵심 흐름의 Django 통합 테스트는 통과했으나 전용 브라우저 런타임 초기화 오류로 실제 브라우저 실행은 작업 4에서 재시도.

핵심 E2E 순서는 A/B 가입 → A 상품 등록 → B 검색·상세 → 1대1 채팅 → B가 A에게 포인트 송금 → 잔액/원장 → 신고 → 관리자 제재 → 일반 사용자 관리자 접근 차단이다.
