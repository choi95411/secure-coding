# Maintenance Log

## 2026-07-16

- PDF 21~36페이지를 텍스트 추출과 PNG 렌더링으로 확인했다.
- WSL/Git/GitHub/Docker/PostgreSQL/Redis 환경을 조사했다.
- Django, Docker PostgreSQL/Redis, 내부 포인트, 로컬 Docker+CI 구성을 승인받았다.
- 인증·프로필·상품·검색과 초기 보안·권한 테스트를 추가했다.
- 마이그레이션 드리프트와 middleware 순서, 개발 키 배포 경고를 발견해 수정했다.

- 내부 포인트 송금·멱등 키·행 잠금·불변 원장과 PostgreSQL 동시성 테스트를 추가했다.
- 중복 신고, 3회 임계치 자동 제재, 관리자 403·사유·전후 상태 감사 로그를 추가했다.

- 관리자 지갑 조정은 잔액·원장·조정 거래·감사 로그를 단일 트랜잭션으로 구현했다.
- PostgreSQL 동시성 본문은 통과했으나 첫 실행에서 스레드 연결 미종료로 테스트 DB 삭제가 실패했다. 스레드별 연결 종료를 추가한 뒤 재실행해 1 passed를 확인했다.

## 2026-07-20

- 전체·1대1 대화, 참여자 제약, 메시지 영속화·숨김 관리와 세션 인증 WebSocket을 구현했다.
- 미인증/비참여자 연결, 신뢰하지 않는 Origin, 메시지 길이, Stored/DOM XSS와 사용자별 메시지 도배를 테스트했다.
- username/IP 원문을 저장하지 않는 HMAC 로그인 실패 제한과 잠금·성공 초기화를 추가했다.
- 최초 대화·로그인 제한 행의 동시 생성 고유 키 충돌을 savepoint와 잠금 재조회로 보강했다.
- 전체 회귀 57 passed, 2 skipped와 migration/Ruff/format/Bandit 통과를 확인했다.
- Docker Desktop 엔진은 기동 단계에서 멈췄지만 WSL Redis 8.0.5를 격리 실행해 실제 채널 계층 테스트 `1 passed`를 확인했다. 브라우저 런타임 샌드박스 오류는 재부팅 후에도 반복되어 Playwright 실제 브라우저 E2E를 작업 4로 이관했다.

## 2026-07-20 작업 4(보고서 제외)

- PostgreSQL 17·Redis 7.4 서비스, 외부 통합 테스트, Ruff·Bandit·pip-audit·deploy check, Docker build를 실행하는 GitHub Actions를 구성했다.
- Playwright Chromium 핵심 사용자 흐름과 상품·채팅·지갑·관리 화면 증빙 아티팩트를 추가했다.
- 신고 대시보드에서 사유·전후 상태가 감사되는 사용자/상품 제재 화면으로 이동할 수 있게 하고 권한 테스트를 추가했다.
- Dependabot 주간 pip·Actions 점검과 커밋 인덱스/전체 Git 이력 비밀 패턴 검사를 추가했다.
- 전체 회귀 `57 passed, 2 skipped`와 로컬 pip check·pip-audit, Git 이력 `.env`·토큰·개인키 검사, Compose 구문, Django deploy check를 통과했다.
- 저장소를 public으로 전환하고 main을 push했다. 첫 CI는 E2E 관리자 스크립트 import 경로 문제로 실패했으며 모듈 실행으로 수정했다.
- 수정 CI에서 PostgreSQL·Redis 전체 테스트, Docker 빌드와 Playwright 핵심 흐름이 모두 통과했다. E2E 화면 4장을 내려받아 한글·레이아웃·민감정보를 시각 확인하고 README에 반영했다.
- GitHub 공식 최신 릴리스에 맞춰 checkout, setup-python, upload-artifact를 v7로 갱신했다.
- Actions v7 최종 main 실행 29720091057에서 모든 단계와 E2E 증빙 업로드가 통과했다. public 저장소 설명·주제를 설정했고 Dependabot 업데이트 PR은 검토 전 자동 병합하지 않았다.
## 2026-07-20 보고서 전 보안·완성도 감사

- Django Admin 직접 상태 변경이 감사 서비스를 우회할 수 있음을 확인해 사용자·프로필·상품·신고·제재·원장·조정·로그 관리 화면을 조회 전용으로 제한했다. 메시지 상태 변경만 사유와 불변 감사 로그를 남기는 기존 통제 흐름으로 허용한다.
- 전용 플랫폼 관리 대시보드에 신고뿐 아니라 사용자·상품 전체 목록과 제재 진입점을 추가했다.
- 원장·조정 거래·제재 이력·관리자 감사 로그의 `QuerySet.update`, `bulk_update`, `delete` 우회를 모델 계층에서 차단했다.
- 서로 다른 대상을 이용한 신고 도배를 막기 위해 신고자 잠금·활성 상태 재검증·시간당 상한을 추가했다.
- 상품 가격, 1회 송금·조정 금액, 수신/조정 후 지갑 잔액의 업무 상한과 DB 가격 제약을 추가했다.
- CSP, Permissions-Policy, Bootstrap SRI를 적용하고 채팅 인라인 스크립트를 정적 파일로 분리했으며 403·404·500 페이지를 추가했다.
- 보강 대상 테스트 `60 passed, 2 skipped`, 회귀 수정 후 관련 테스트 `49 passed, 1 skipped`, Ruff·format·migration drift·Django check·Bandit을 통과했다. 전체 검사에서 읽기 전용 공통화가 감사되는 메시지 상태 변경까지 막는 회귀 1건을 발견해 예외 흐름을 복원하고 관련 테스트를 통과했다.- 최종 로컬 전체 회귀 `67 passed, 2 skipped`와 Ruff·format·Bandit·migration drift·pip check·pip-audit·deploy check·비밀 이력·Compose 구문 검사를 통과했다.
- Docker Desktop 29.2.1을 기동해 이미지를 실제 빌드했으며 `appuser` 비루트 실행과 컨테이너 내부 Django check 통과를 확인했다.- 첫 보안 강화 CI 29722926398은 코드·보안·Docker·PostgreSQL·Redis 테스트를 모두 통과했으나, `DEBUG=false`에서 채팅 정적 파일이 수집되지 않아 Playwright 전송 버튼 단언에서 실패했다.
- Dockerfile·Compose·E2E 시작 절차에 `collectstatic`을 추가하고 관리자 화면 제목 단언을 갱신했다. 정적 파일 발견 테스트, 새 Docker 이미지의 `/app/staticfiles/chat/chat.js`, 전체 `68 passed, 2 skipped`를 확인했다.- 수정 CI 29723526957에서 migration, Ruff, Bandit, pip-audit, 비밀 이력, Docker, deploy check, PostgreSQL·Redis 전체 테스트, Playwright 핵심 흐름과 증빙 업로드가 모두 통과했다.- 남아 있던 CSP `style-src unsafe-inline`도 제거했다. 로그인·가입·상품 카드·채팅 높이 스타일을 `css/app.css`로 이동하고 템플릿 인라인 스타일 0건, CSS 정적 탐색, CSP 회귀 테스트를 확인했다.
