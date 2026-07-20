# Threat Model

보호 자산은 계정·세션, 비공개 상품, 채팅, 신고·제재, 지갑 잔액·원장, 관리자 감사 기록이다.

| 위협 | 통제 |
|---|---|
| SQL Injection | Django ORM과 선택지 allowlist, 원시 SQL 금지 |
| Stored/Reflected/DOM XSS | 템플릿 autoescape, DOM `textContent`, 외부 정적 스크립트, CSP·SRI, 길이 제한, 회귀 테스트 |
| CSRF·세션 고정 | CSRF, POST 상태 변경, login 세션 키 회전, HttpOnly/SameSite |
| IDOR·권한 상승 | 서버 로그인·소유자·참여자·staff 검사와 403/404/4403 테스트 |
| 로그인 무차별 대입 | HMAC(username+IP) 실패 창·잠금, 성공 초기화 |
| 악성 업로드 | UUID 경로, 확장자·MIME·5MB·Pillow 내용 검증 |
| WebSocket 위조·도배 | 허용 Origin, 세션·상태·참여자 검사, 길이와 DB 행 잠금 Rate Limit |
| 송금 중복·경쟁·정수 남용 | PostgreSQL transaction, 정렬된 행 잠금, 고유 멱등 키, 금액·잔액 상한, QuerySet 우회 방지 불변 원장 |
| 신고 도배 | 사용자/대상 고유 제약, 신고자 잠금, 활성 상태 검사, 시간당 상한과 제재 임계치 |
| 관리자 남용·감사 우회 | staff 권한, Django Admin 직접 변경 차단, 전용 서비스 사유 필수, 전후 상태와 QuerySet 수정 불가 감사 로그 |
| 비밀 유출 | `.env` ignore, push 전 의존성·Git 이력 검사 |

신뢰 경계는 브라우저/HTTP·WebSocket 입력, Django 애플리케이션, PostgreSQL 영구 저장소, Redis 비영구 메시지 전달, 관리자 계정 사이에 둔다. Redis 장애는 실시간 전달에 영향을 주지만 DB에 저장된 업무 기록의 원본을 변경하지 않는다.
