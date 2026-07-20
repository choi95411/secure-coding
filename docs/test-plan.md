# Test Plan

계층은 모델 제약, Form/서비스 단위, View·DB 통합, 인증·권한, 파일 업로드, WebSocket, PostgreSQL 트랜잭션·동시성, Playwright E2E다.

- 작업 1: 가입·중복·비밀번호 해시·차단 로그인·POST 로그아웃·마이페이지 인증·본인 프로필·XSS, 상품 CRUD·업로드 검증·소유권·소프트 삭제·공개 범위, 검색 필터·정렬·빈 값·SQLi 문자열·Reflected XSS.
- 작업 2: 지갑 초기 포인트, 양의 정수·자기 송금·비활성 수신자·잔액 초과, 멱등 재요청, 실패 롤백, 불변 원장, 관리자 조정 및 감사, PostgreSQL 별도 연결 동시 송금. 신고 중복·자동 제재·복구와 일반 사용자 관리자 접근 차단.
- 작업 3: 전체/1대1 대화 정규화, 비참여자 차단, 숨김 메시지, XSS escape, WebSocket 미인증·비참여자 거절, 메시지 길이·Rate Limit·영속화·브로드캐스트, 실제 ASGI 세션 쿠키 인증과 신뢰하지 않는 Origin 차단, 로그인 실패 잠금·성공 초기화·식별자 비식별화, 핵심 A/B 통합 흐름.

## 최근 결과

- 보고서 전 보안 보강 대상 회귀: `60 passed, 2 skipped`; 관리자 공통화 회귀 수정 후 관련 `49 passed, 1 skipped` (2026-07-20).
- 최종 SQLite 전체 회귀: `68 passed, 2 skipped`; skip된 PostgreSQL·Redis 외부 통합 2건은 CI에서 실행한다.
- Ruff lint/format, migration drift, Bandit: 통과.
- PostgreSQL 송금 동시성: 실제 `postgres:17-alpine` 환경에서 `1 passed`.
- Redis 채널 계층 테스트: WSL Redis 8.0.5를 56379 포트에서 영속화 없이 격리 실행해 `1 passed`.
- Playwright 브라우저 E2E: GitHub Actions에서 핵심 전체 흐름과 네 화면 증빙 생성까지 통과.

핵심 E2E 순서는 A/B 가입 → A 상품 등록 → B 검색·상세 → 1대1 채팅 → B가 A에게 포인트 송금 → 잔액/원장 → 신고 → 관리자 제재 → 일반 사용자 관리자 접근 차단이다.

## GitHub Actions 검증

[보안 보강 최종 main CI 29723526957](https://github.com/choi95411/secure-coding/actions/runs/29723526957)에서 Actions v7 전 단계가 통과했다. Ubuntu, Python 3.13, PostgreSQL 17, Redis 7.4 서비스에서 migration drift, Ruff, Bandit, pip-audit, Django deploy check, 전체 pytest(외부 통합 포함), Docker Compose 구성·이미지 빌드를 수행한다. 이후 Daphne를 실행하고 Playwright Chromium으로 가입 → 상품 등록·검색 → 1대1 WebSocket 채팅 → 송금·양측 잔액 → 신고 → 관리자 제재 → 일반 사용자 관리자 403을 검증하며 네 화면과 서버 로그를 `e2e-evidence` 아티팩트로 보존한다.

## 보고서 전 보안 회귀 추가

- Django Admin 사용자·상품·신고 직접 변경 403 및 원본 상태 불변
- 원장·조정·제재·감사 로그의 인스턴스 및 QuerySet 수정/삭제 차단
- 비활성 사용자의 신고와 서로 다른 대상 시간당 신고 도배 차단
- 상품 가격, 송금·조정 1회 금액, 지갑 잔액 상한
- CSP에서 인라인 스크립트 금지, Permissions-Policy, 외부 정적 채팅 스크립트
- 사용자 친화적 403·404와 내부 Traceback 비노출
- `DEBUG=false` 환경에서 `collectstatic` 후 `chat/chat.js` 발견·Docker 이미지 포함을 검증한다.
