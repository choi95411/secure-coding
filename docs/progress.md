# Progress

- 완료: PDF 최소 기능 전체, 인증·상품·검색, 송금·불변 원장·동시성, 신고·제재·감사, 전체·1대1 채팅, 관리자 통합 관리, README, public GitHub, CI/Dependabot/Playwright E2E
- 현재 작업: 첫 CI에서 발견한 정적 파일 배포 회귀 수정 완료, 재커밋·CI 최종 확인
- 남음: GitHub Actions 최종 통과 확인, 이후 사용자 요청 시 최종 보고서 원본·PDF와 시각 검증
- 최근 테스트: 최종 로컬 `68 passed, 2 skipped`; Ruff·format·migration drift·Bandit·pip check·pip-audit·deploy check·비밀 이력·Compose 통과; Docker 29.2.1 이미지 빌드, 비루트 `appuser`, 컨테이너 Django check 통과
- 주요 결정: Django Admin은 조회 전용으로 제한하고 상태 변경은 사유·전후 값이 감사되는 전용 서비스만 사용; 신고 시간당 10회, 포인트 1회 10억, 지갑 최대 9경 포인트; CSP/Permissions-Policy 적용
- 알려진 문제: 보고서는 의도적으로 미작성; 운영 배포는 범위 제외; 로컬 SQLite에서는 PostgreSQL·Redis 외부 통합 2건이 skip되며 GitHub Actions에서 실행
- 다음 실행 명령: `.venv/bin/pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check . && bash scripts/scan_secrets.sh`
