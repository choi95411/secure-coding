# HTTP and WebSocket Design

- `GET /`: 공개 상품 검색·필터·정렬·페이지네이션
- `GET/POST /accounts/signup/`, `GET/POST /accounts/login/`, `POST /accounts/logout/`
- `GET /accounts/me/`, `GET/POST /accounts/me/profile/`, `GET/POST /accounts/me/password/`
- `GET /accounts/users/<username>/`
- `GET/POST /products/new/`, `GET /products/<id>/`, `GET/POST /products/<id>/edit/`, `POST /products/<id>/delete/`

상태 변경 HTML 요청은 POST와 CSRF 토큰을 요구한다. 객체 미노출은 404, 인증된 비소유자의 변경은 403을 사용한다. 후속 WebSocket은 `/ws/chat/<conversation-id>/`에서 세션 인증과 참여자 검사를 수행한다.
