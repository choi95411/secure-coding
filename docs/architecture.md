# Architecture

Django 서버 렌더링 모놀리스와 PostgreSQL을 기본으로 사용한다. Redis는 Channels의 프로세스 간 메시지 전달에만 사용하며 영구 업무 데이터의 원본으로 사용하지 않는다. 요청은 URL/View/Form을 거쳐 서비스·ORM으로 전달되고 템플릿은 autoescape를 유지한다. 인증은 Django 세션, 상태·소유권·참여자·관리자 권한은 각 서버 엔드포인트에서 재검증한다.

- 공개: 상품 목록·상세, 활성 사용자 프로필, 가입·로그인
- 인증: 마이페이지, 상품 변경, 송금, 신고, 전체 채팅
- 소유자/참여자: 상품 수정·삭제, 1대1 대화 열람과 WebSocket 연결
- 관리자: 제재, 복구, 메시지 상태 관리, 조정 거래, 전체 감사 조회

ASGI는 `AllowedHostsOriginValidator` → Channels 세션 인증 → WebSocket URL router 순서다. 메시지는 DB에 먼저 저장한 뒤 Redis channel layer로 브로드캐스트하며, 사용자 행 잠금으로 동시 전송도 분당 제한을 우회하지 못하게 한다. 로그인 실패 제한 키는 username/IP 원문 대신 Django SECRET_KEY 기반 HMAC을 저장한다.

외부 결제, 카드·은행, 마이크로서비스와 별도 SPA는 범위 밖이다.
