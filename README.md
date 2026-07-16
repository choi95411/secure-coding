# Tiny Second-hand Shopping Platform

WhiteHat School 시큐어 코딩 과제를 위한 교육용 중고거래 플랫폼입니다. 현재 인증, 프로필, 상품 CRUD, 안전한 이미지 업로드와 상품 검색을 구현했습니다. 송금은 실제 화폐가 아닌 내부 테스트 포인트만 사용합니다.

## 주요 구성

Django 5.2 LTS, PostgreSQL, Redis, Channels, Bootstrap, pytest, Playwright, Docker Compose, GitHub Actions 기반의 서버 렌더링 모놀리스입니다.

## Docker 실행

```bash
cp .env.example .env
# DJANGO_SECRET_KEY와 DB 비밀번호를 변경
docker compose up --build
```

`http://localhost:8000`에 접속합니다. 현재 조사 환경은 Docker daemon과 Compose 플러그인이 중지/누락 상태이므로 실행 전 Docker Desktop과 Compose 복구가 필요합니다.

## 비 Docker 실행

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

DATABASE_URL을 생략하면 개발·단위 테스트용 SQLite를 사용합니다. PostgreSQL과 Redis 연결은 `.env.example`을 참고하세요.

## 테스트

```bash
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/bandit -c pyproject.toml -r config users products
```

상세 설계와 추적표는 `docs/requirements.md`, `docs/architecture.md`, `docs/security-checklist.md`, `docs/test-plan.md`에 있습니다.

## 알려진 제한사항

현재는 작업 1 범위입니다. 지갑·원장·송금, 신고·제재·감사, 전체·1대1 채팅, E2E와 최종 보고서는 후속 작업에서 구현합니다. 외부 결제와 실제 화폐는 취급하지 않습니다.