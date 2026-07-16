# Requirements and Traceability

상태: `DONE` 구현·관련 테스트 통과, `PLANNED` 후속 작업 예정.

| ID | 요구사항 / 행위자 | 선행·정상 흐름 | 실패·권한·보안 | 인수 조건 | 구현 / 테스트 | 상태 |
|---|---|---|---|---|---|---|
| AUTH-01 | 회원가입·로그인·로그아웃 / 방문자·사용자 | 고유 아이디와 강한 비밀번호로 가입 후 세션 로그인, POST 로그아웃 | 중복·약한 입력 거절, 휴면·차단 로그인 거절, CSRF, 비밀번호 해시 | 정상·중복·차단·로그아웃 메서드 테스트 | `users/forms.py`, `users/views.py` / `users/tests/test_auth.py` | DONE |
| USER-01 | 사용자 조회·프로필·마이페이지 / 사용자 | 활성 사용자 공개 프로필 조회, 본인 소개·비밀번호 변경 | 비로그인 마이페이지 차단, 본인 프로필만 수정, 출력 escape | 인증·소유·Stored XSS 회귀 통과 | `users/` / `users/tests/test_auth.py` | DONE |
| PROD-01 | 상품 등록·목록·상세·수정·삭제 / 사용자 | 로그인 사용자가 DB 상품과 검증된 이미지 등록, 소유자가 수정·소프트 삭제 | 비로그인 거절, IDOR 403, 비공개·차단·삭제 404, 악성 업로드 거절 | 정상·실패·권한·파일 테스트 통과 | `products/` / `products/tests/test_products.py` | DONE |
| SEARCH-01 | 상품 검색 / 모두 | 제목·설명 검색, 공개 판매 상태 필터, 정렬, 12개 페이지네이션 | ORM 바인딩, XSS escape, 비공개·차단·삭제 제외 | 빈 값·SQLi 문자열·XSS·필터 테스트 | `products/views.py` / `ProductSearchTests` | DONE |
| CHAT-01 | 전체 및 1대1 실시간 채팅 / 활성 사용자 | 인증 WebSocket, DB 이력, 참여자 전송 | 미인증·비참여자 거절, Rate Limit | WebSocket 정상·실패·권한 테스트 | 후속 `chat/` | PLANNED |
| REPORT-01 | 사용자·상품 신고 / 활성 사용자 | 대상·사유 신고, 중복/도배 제한 | 자기 대상·중복·비활성 거절 | 신고·임계치·경쟁 테스트 | 후속 `moderation/` | PLANNED |
| MOD-01 | 상품 차단·사용자 휴면/차단/복구 / 관리자 | 처리 사유와 전후 상태 감사 기록 | 일반 사용자 403, 감사 로그 변경 금지 | 제재·복구·관리자 권한 테스트 | 후속 `moderation/` | PLANNED |
| PAY-01 | 내부 포인트 송금 / 활성 사용자 | 지갑·불변 원장·단일 트랜잭션·행 잠금·멱등 키 | 양의 정수, 자기 송금·초과 잔액·중복·비활성 거절, 전체 롤백 | 동시 송금 시 음수 불가, 원장 정합성 | 후속 `wallets/` | PLANNED |
| ADMIN-01 | 플랫폼 전체 관리 / 관리자 | 사용자·프로필·상품·신고·제재·메시지·송금·조정·감사 조회/처리 | 서버 측 staff 권한, 작업 전후·사유 기록 | 일반 사용자 URL 직접 호출 403 | Django Admin + 후속 서비스 | PLANNED |
| DOC-01 | 공개 GitHub·README·보고서 / 제출자 | 실행 절차, 보안 약점, 테스트 결과, 링크, 지정 파일명 | 비밀·개인정보·임시 파일 제외 | public 저장소·CI·렌더링 보고서 확인 | `README.md`, `docs/`, 후속 보고서 | PLANNED |

PDF 35페이지의 가입, 상품, 소통, 악성 대상 차단, 송금, 검색, 관리자 관리 항목은 각각 AUTH/USER, PROD, CHAT, REPORT/MOD, PAY, SEARCH, ADMIN에 일대일 대응한다.
