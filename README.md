# Tiny Second-hand Shopping Platform

WhiteHat School 시큐어 코딩 과제를 위한 교육용 중고거래 플랫폼입니다. 인증·프로필, 상품 CRUD·안전한 이미지·검색, 내부 포인트 송금과 불변 원장, 신고·제재·감사, 전체 및 1대1 실시간 채팅을 제공합니다. 실제 화폐나 외부 결제는 사용하지 않습니다.

## 주요 구성

Django 5.2 LTS 서버 렌더링 모놀리스, PostgreSQL, Redis/Channels, Bootstrap, pytest, Playwright, Docker Compose, GitHub Actions를 사용합니다. 서버에서 객체 소유권·대화 참여자·계정 상태·관리자 권한을 검증합니다.

## Docker 실행

```bash
cp .env.example .env
# DJANGO_SECRET_KEY와 DB 비밀번호를 변경

docker compose up --build
```

마이그레이션 후 `http://localhost:8000`에 접속합니다. 관리자 계정은 다음처럼 만듭니다.

```bash
docker compose exec web python manage.py createsuperuser
```

## 비 Docker 실행

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

SQLite는 단위 개발용입니다. 송금 동시성 검증과 실제 실행은 `.env.example`의 PostgreSQL `DATABASE_URL`을 사용하세요. 실시간 채팅은 `REDIS_URL`의 Redis가 필요합니다. 신규 사용자는 기본 10,000 테스트 포인트를 받으며 `INITIAL_WALLET_POINTS`로 조정할 수 있습니다.

## 테스트와 보안 검사

```bash
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/bandit -c pyproject.toml -r config users products wallets moderation adjustments chat security_controls
```

외부 서비스 통합 테스트는 명시적으로 활성화합니다.

```bash
RUN_POSTGRES_TESTS=1 .venv/bin/pytest wallets/tests/test_postgres_concurrency.py
RUN_REDIS_TESTS=1 .venv/bin/pytest chat/tests/test_redis_integration.py
```

환경변수는 `.env.example`에 설명되어 있습니다. `.env`, 비밀 키, DB 비밀번호와 개인 토큰은 커밋하지 않습니다. 운영/제출 구성에서는 강한 `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, HTTPS와 secure cookie 설정을 사용해야 합니다.

상세 요구사항, 설계, 위협 모델과 테스트 결과는 `docs/requirements.md`, `docs/architecture.md`, `docs/database-design.md`, `docs/threat-model.md`, `docs/security-checklist.md`, `docs/test-plan.md`를 참고하세요.

## 알려진 제한사항

현재 교육용 플랫폼이며 외부 결제·실물 화폐·추천 시스템은 지원하지 않습니다. Redis 채널 계층은 WSL 로컬 Redis로 통합 검증했습니다. Playwright 실제 브라우저 E2E는 브라우저 런타임 복구 후 재검증해야 합니다. GitHub Actions, 공개 저장소 전환, 화면 예시와 최종 보고서는 작업 4에서 마감합니다.
