# Threat Model

보호 자산은 계정·세션, 비공개 상품, 채팅, 신고·제재, 지갑 잔액·원장, 관리자 감사 기록이다.

| 위협 | 통제 |
|---|---|
| SQL Injection | Django ORM과 선택지 allowlist, 원시 SQL 금지 |
| Stored/Reflected XSS | 템플릿 autoescape, 길이 제한, 회귀 테스트 |
| CSRF·세션 고정 | CSRF, POST 상태 변경, login 세션 키 회전, HttpOnly/SameSite |
| IDOR·권한 상승 | 서버 로그인·소유자·참여자·staff 검사와 403/404 테스트 |
| 악성 업로드 | UUID 경로, 확장자·MIME·5MB·Pillow 내용 검증 |
| 송금 중복·경쟁 | PostgreSQL transaction, 행 잠금, 고유 멱등 키, 불변 원장 |
| 신고·메시지 도배 | 사용자/대상/시간 기반 Redis+DB 제한 |
| 관리자 남용 | 사유 필수, 전후 상태와 관리자 감사 로그 |
| 비밀 유출 | `.env` ignore, push 전 Git 이력 검사 |
