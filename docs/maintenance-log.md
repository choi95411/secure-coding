# Maintenance Log

## 2026-07-16

- PDF 21~36페이지를 텍스트 추출과 PNG 렌더링으로 확인했다.
- WSL/Git/GitHub/Docker/PostgreSQL/Redis 환경을 조사했다.
- Django, Docker PostgreSQL/Redis, 내부 포인트, 로컬 Docker+CI 구성을 승인받았다.
- 인증·프로필·상품·검색과 초기 보안·권한 테스트를 추가했다.
- 마이그레이션 드리프트와 middleware 순서, 개발 키 배포 경고를 발견해 수정했다.

- 내부 포인트 송금·멱등 키·행 잠금·불변 원장과 PostgreSQL 동시성 테스트를 추가했다.
- 중복 신고, 3회 임계치 자동 제재, 관리자 403·사유·전후 상태 감사 로그를 추가했다.

- 관리자 지갑 조정은 잔액·원장·조정 거래·감사 로그를 단일 트랜잭션으로 구현했다.
- PostgreSQL 동시성 본문은 통과했으나 첫 실행에서 스레드 연결 미종료로 테스트 DB 삭제가 실패했다. 스레드별 연결 종료를 추가한 뒤 재실행해 1 passed를 확인했다.

## 2026-07-20

- 전체·1대1 대화, 참여자 제약, 메시지 영속화·숨김 관리와 세션 인증 WebSocket을 구현했다.
- 미인증/비참여자 연결, 신뢰하지 않는 Origin, 메시지 길이, Stored/DOM XSS와 사용자별 메시지 도배를 테스트했다.
- username/IP 원문을 저장하지 않는 HMAC 로그인 실패 제한과 잠금·성공 초기화를 추가했다.
- 최초 대화·로그인 제한 행의 동시 생성 고유 키 충돌을 savepoint와 잠금 재조회로 보강했다.
- 전체 회귀 56 passed, 2 skipped와 migration/Ruff/format/Bandit 통과를 확인했다.
- Docker Desktop 엔진은 기동 단계에서 멈췄지만 WSL Redis 8.0.5를 격리 실행해 실제 채널 계층 테스트 `1 passed`를 확인했다. 브라우저 런타임 샌드박스 오류는 재부팅 후에도 반복되어 Playwright 실제 브라우저 E2E를 작업 4로 이관했다.
