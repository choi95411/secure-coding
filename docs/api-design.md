# HTTP and WebSocket Design

- `GET /`: 공개 상품 검색·필터·정렬·페이지네이션
- `GET/POST /accounts/signup/`, `GET/POST /accounts/login/`, `POST /accounts/logout/`
- `GET /accounts/me/`, `GET/POST /accounts/me/profile/`, `GET/POST /accounts/me/password/`
- `GET /accounts/users/<username>/`
- `GET/POST /products/new/`, `GET /products/<id>/`, `GET/POST /products/<id>/edit/`, `POST /products/<id>/delete/`
- `GET /wallet/`, `GET/POST /wallet/transfer/`
- `POST /reports/users/<username>/`, `POST /reports/products/<id>/`
- `GET /moderation/`, 관리자 제재·복구 POST 엔드포인트
- `GET /chat/`, `GET /chat/global/`, `POST /chat/direct/<username>/`, `GET /chat/<id>/`
- `WS /ws/chat/<conversation-id>/`: Django 세션 인증, Origin 검증, 활성 상태와 참여자 검증, JSON `{message}` 전송

상태 변경 HTML 요청은 POST와 CSRF 토큰을 요구한다. 객체 미노출은 404, 인증된 비소유자/비참여자는 403, WebSocket 미인증/권한 위반은 각각 4401/4403을 사용한다. 메시지 오류는 `invalid_message`, `invalid_length`, `rate_limited` 코드로 반환한다.
