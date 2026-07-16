# ADR-0001: Django Monolith with PostgreSQL and Redis

- 상태: 승인
- 날짜: 2026-07-16

Django 5.2 서버 렌더링 모놀리스, PostgreSQL, Redis/Channels, Bootstrap, pytest/Playwright, Docker Compose와 GitHub Actions를 사용한다. 송금은 내부 테스트 포인트다. Django의 인증·ORM·CSRF·관리자 기능을 재사용하고 PostgreSQL 행 잠금으로 송금을 검증한다. 별도 SPA·마이크로서비스·외부 결제는 제외한다.
