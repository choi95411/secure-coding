# Security Checklist

- [x] ORM과 SQLi 문자열 검색 회귀
- [x] autoescape, DOM `textContent`, Stored/Reflected XSS 테스트
- [x] CSRF middleware 및 상태 변경 POST
- [x] 상품 소유권과 채팅 참여자 IDOR 403/4403 테스트
- [x] Django 비밀번호 해시·강도 검증
- [x] HttpOnly/SameSite, X-Frame-Options, nosniff
- [x] 이미지 확장자·MIME·크기·내용·UUID 경로 검증
- [x] Debug/SSL/HSTS 환경변수 분리
- [x] 원문 계정/IP를 저장하지 않는 로그인 무차별 대입 제한
- [x] WebSocket 세션 인증·Origin·참여자·길이·Rate Limit
- [x] 신고 중복 방지·제재 임계치·자동 상품 차단/사용자 휴면
- [x] 송금 멱등·롤백·불변 원장·PostgreSQL 동시성 및 관리자 조정 거래
- [x] 사용자·상품 제재·지갑 조정 관리자 권한 및 불변 감사 로그 회귀
- [x] pip check·pip-audit 의존성 검사와 전체 Git 이력 토큰·개인키·`.env` 추적 검사
- [x] CSP·Permissions-Policy·CDN SRI 및 인라인 채팅 스크립트 제거
- [x] Django Admin 직접 변경 차단과 감사 서비스 강제
- [x] 원장·조정·제재·감사 QuerySet 수정/삭제 우회 차단
- [x] 사용자별 시간당 신고 제한과 비활성 사용자 신고 차단
- [x] 상품 가격·송금·조정·지갑 잔액 상한 검증
- [x] 사용자 친화적 403·404·500 응답과 상세 오류 비노출

## 발견 및 수정 기록

- `SEC-001` 계정 상태 middleware가 message middleware보다 앞서면 제재 계정 요청에서 메시지 저장소 오류가 날 수 있었다. 순서를 교정하고 회귀 테스트를 통과했다. CWE-20.
- `SEC-002` 초기 개발 기본 SECRET_KEY가 배포 검사 기준보다 짧았다. 긴 개발 표식 값과 `.env` 교체 절차, HTTPS/HSTS 환경변수를 추가했다. 운영은 별도 난수 키를 요구한다. CWE-798.
- `SEC-003` 로그인 실패 제한이 없으면 비밀번호 무차별 대입이 가능했다. username과 IP를 HMAC 처리한 키로 실패 창·잠금을 DB에 기록하고 성공 시 삭제하도록 구현했다. 원문 개인정보는 저장하지 않으며 잠금·초기화 테스트를 통과했다. CWE-307.
- `SEC-004` 채팅은 HTTP 권한만으로는 WebSocket 직접 연결과 메시지 도배를 막을 수 없다. 세션 인증, 허용 Origin, 연결 후에도 반복하는 활성 계정·대화 참여자 검사, 길이 제한, 사용자 행 잠금 기반 분당 제한을 추가했고 ASGI/WebSocket 회귀 테스트를 통과했다. CWE-284, CWE-770.
- `SEC-005` 대화와 로그인 제한 행의 최초 생성이 동시에 발생하면 고유 제약 오류가 노출될 수 있었다. 중첩 savepoint에서 충돌을 격리하고 잠금 재조회하도록 보강했다. CWE-362.
- `SEC-006` 메시지 상태를 Django Admin에서 변경할 수 있었지만 사유와 전후 상태가 감사 로그에 남지 않았다. 상태 변경 사유를 필수화하고 단일 트랜잭션에서 불변 `AdminAuditLog`를 생성하며 대화·멤버는 읽기 전용으로 제한했다. CWE-778.

- `SEC-007` Django Admin에서 사용자·상품·신고를 직접 바꾸면 전용 제재 서비스와 사유·전후 상태 감사를 우회할 수 있었다. 해당 모델 관리 화면을 조회 전용으로 만들고, 사용자·상품 전체 목록을 감사되는 전용 관리 대시보드에 추가했으며 직접 POST가 403이고 데이터가 불변임을 검증했다. CWE-284, CWE-778.
- `SEC-008` 불변 레코드의 인스턴스 `save/delete`는 차단했지만 `QuerySet.update()`가 이를 우회할 수 있었다. 원장·지갑 조정·제재 이력·관리자 감사 로그의 `update/bulk_update/delete`를 모델 계층에서 거절하고 회귀 테스트를 추가했다. CWE-664.
- `SEC-009` 동일 대상 중복 신고는 막았지만 서로 다른 대상을 연속 신고하는 도배가 가능했다. 신고자 행 잠금, 활성 계정 재검증, 시간당 사용자별 신고 상한을 추가했다. CWE-770.
- `SEC-010` 기본 보안 헤더에 CSP와 Permissions-Policy가 없고 채팅 템플릿에 인라인 JavaScript가 있었다. 스크립트를 정적 파일로 분리하고 엄격한 `script-src 'self'`, `object-src 'none'`, `frame-ancestors 'none'`, Permissions-Policy와 Bootstrap SRI를 적용했다. CWE-693.
- `SEC-011` 상품 가격과 포인트 거래가 DB 정수 범위 외 별도 업무 상한을 갖지 않았다. 상품 DB 제약·폼 검증, 송금/조정 1회 한도와 지갑 최대 잔액 검사를 서비스 계층에 추가하고 초과 요청 회귀 테스트를 통과했다. CWE-20.
- `SEC-012` CSP 적용 후 채팅 JavaScript를 정적 파일로 분리했지만 `DEBUG=false` E2E/Docker 시작 절차가 `collectstatic`을 실행하지 않아 실시간 채팅 버튼이 비활성화됐다. CI 브라우저 테스트에서 발견했으며, 이미지 빌드·Compose·E2E 시작에 정적 파일 수집을 추가하고 `finders`, Docker 이미지 파일 존재, 전체 회귀로 검증했다. CWE-16.
