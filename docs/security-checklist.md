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
- [ ] 의존성 취약점과 전체 Git 이력 비밀 검사(작업 4)

## 발견 및 수정 기록

- `SEC-001` 계정 상태 middleware가 message middleware보다 앞서면 제재 계정 요청에서 메시지 저장소 오류가 날 수 있었다. 순서를 교정하고 회귀 테스트를 통과했다. CWE-20.
- `SEC-002` 초기 개발 기본 SECRET_KEY가 배포 검사 기준보다 짧았다. 긴 개발 표식 값과 `.env` 교체 절차, HTTPS/HSTS 환경변수를 추가했다. 운영은 별도 난수 키를 요구한다. CWE-798.
- `SEC-003` 로그인 실패 제한이 없으면 비밀번호 무차별 대입이 가능했다. username과 IP를 HMAC 처리한 키로 실패 창·잠금을 DB에 기록하고 성공 시 삭제하도록 구현했다. 원문 개인정보는 저장하지 않으며 잠금·초기화 테스트를 통과했다. CWE-307.
- `SEC-004` 채팅은 HTTP 권한만으로는 WebSocket 직접 연결과 메시지 도배를 막을 수 없다. 세션 인증, 허용 Origin, 연결 후에도 반복하는 활성 계정·대화 참여자 검사, 길이 제한, 사용자 행 잠금 기반 분당 제한을 추가했고 ASGI/WebSocket 회귀 테스트를 통과했다. CWE-284, CWE-770.
- `SEC-005` 대화와 로그인 제한 행의 최초 생성이 동시에 발생하면 고유 제약 오류가 노출될 수 있었다. 중첩 savepoint에서 충돌을 격리하고 잠금 재조회하도록 보강했다. CWE-362.
- `SEC-006` 메시지 상태를 Django Admin에서 변경할 수 있었지만 사유와 전후 상태가 감사 로그에 남지 않았다. 상태 변경 사유를 필수화하고 단일 트랜잭션에서 불변 `AdminAuditLog`를 생성하며 대화·멤버는 읽기 전용으로 제한했다. CWE-778.
