# Requirements and Traceability

상태: `DONE` 구현·관련 테스트 통과, `IN_PROGRESS` 구현되었으나 외부 통합 검증 잔여, `PLANNED` 후속 작업 예정.

| ID | 요구사항 / 행위자 | 선행·정상 흐름 | 실패·권한·보안 | 인수 조건 | 구현 / 테스트 | 상태 |
|---|---|---|---|---|---|---|
| AUTH-01 | 회원가입·로그인·로그아웃 / 방문자·사용자 | 고유 아이디와 강한 비밀번호로 가입 후 세션 로그인, POST 로그아웃 | 중복·약한 입력 거절, 휴면·차단 로그인 거절, CSRF, 비밀번호 해시, 해시 식별자 기반 로그인 제한 | 정상·중복·차단·무차별 대입·로그아웃 메서드 테스트 | `users/`, `security_controls/` / 인증·로그인 제한 테스트 | DONE |
| USER-01 | 사용자 조회·프로필·마이페이지 / 사용자 | 활성 사용자 공개 프로필 조회, 본인 소개·비밀번호 변경 | 비로그인 마이페이지 차단, 본인 프로필만 수정, 출력 escape | 인증·소유·Stored XSS 회귀 통과 | `users/` / `users/tests/test_auth.py` | DONE |
| PROD-01 | 상품 등록·목록·상세·수정·삭제 / 사용자 | 로그인 사용자가 DB 상품과 검증된 이미지 등록, 소유자가 수정·소프트 삭제 | 비로그인 거절, IDOR 403, 비공개·차단·삭제 404, 악성 업로드 거절 | 정상·실패·권한·파일 테스트 통과 | `products/` / `products/tests/test_products.py` | DONE |
| SEARCH-01 | 상품 검색 / 모두 | 제목·설명 검색, 공개 판매 상태 필터, 정렬, 12개 페이지네이션 | ORM 바인딩, XSS escape, 비공개·차단·삭제 제외 | 빈 값·SQLi 문자열·XSS·필터 테스트 | `products/views.py` / `ProductSearchTests` | DONE |
| CHAT-01 | 전체 및 1대1 실시간 채팅 / 활성 사용자 | 세션 인증 WebSocket, DB 이력, 전체 또는 정확한 두 참여자 전송 | 미인증 4401·비참여자 4403, 1~1000자, DB 행 잠금 사용자별 Rate Limit, DOM `textContent` | HTTP·ASGI 세션·Origin·WebSocket 정상/실패/권한/Rate Limit 테스트 | `chat/`, `config/asgi.py` / `chat/tests/` | DONE |
| REPORT-01 | 사용자·상품 신고 / 활성 사용자 | 대상·사유 신고, 대상 잠금, 중복/사용자별 시간당 도배 제한 | 자기 대상·중복·비활성·상한 초과 거절 | 신고·임계치·서로 다른 대상 도배 테스트 | `moderation/` / `moderation/tests/test_moderation.py` | DONE |
| MOD-01 | 상품 차단·사용자 휴면/차단/복구 / 관리자 | 처리 사유와 전후 상태 감사 기록 | 일반 사용자 403, 감사 로그 변경 금지 | 제재·복구·관리자 권한 테스트 | `moderation/` / `moderation/tests/test_moderation.py` | DONE |
| PAY-01 | 내부 포인트 송금 / 활성 사용자 | 지갑·불변 원장·단일 트랜잭션·정렬된 행 잠금·멱등 키 | 양의 정수, 자기 송금·잔액/1회/지갑 상한·중복·비활성 거절, 전체 롤백 | 동시 송금 시 음수 불가, QuerySet 수정 차단, 원장 정합성 | `wallets/`, `adjustments/` / 송금·조정·불변성·PostgreSQL 동시성 테스트 | DONE |
| ADMIN-01 | 플랫폼 전체 관리 / 관리자 | 전용 대시보드에서 사용자·상품·신고·제재, 조회 전용 Admin에서 프로필·송금·원장·조정·감사 조회 | 서버 측 staff 권한, Admin 직접 변경 403, 상태 변경 사유·전후 값 감사, 원장/감사 QuerySet 수정 금지 | 일반 사용자 URL 및 관리자 우회 POST 차단 | Django Admin + `moderation/`, `adjustments/`, `chat/admin.py` / 관리자 권한·우회·불변성 테스트 | DONE |
| DOC-01 | 공개 GitHub·README·보고서 / 제출자 | 실행 절차, 보안 약점, 테스트 결과, 링크, 지정 파일명 | 비밀·개인정보·임시 파일 제외 | public 저장소·CI·렌더링 보고서 확인 | `README.md`, `.github/`, `docs/`, 후속 보고서 | IN_PROGRESS |

PDF 35페이지의 가입, 상품, 소통, 악성 대상 차단, 송금, 검색, 관리자 관리 항목은 각각 AUTH/USER, PROD, CHAT, REPORT/MOD, PAY, SEARCH, ADMIN에 일대일 대응한다.
