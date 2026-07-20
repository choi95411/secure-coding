# Submission Checklist

## 코드와 기능

- [x] PDF 35페이지 최소 기능 구현 및 요구사항 추적
- [x] 서버 측 인증·소유권·참여자·관리자 권한 검증
- [x] PostgreSQL 송금 동시성 및 Redis 채널 계층 실검증
- [x] 정상·실패·비로그인·권한 위반·보안 회귀 테스트
- [x] GitHub Actions PostgreSQL·Redis·Playwright 구성
- [x] Docker와 비 Docker 실행 절차

## 공개 전 검사

- [x] `.env`, DB 비밀번호, 토큰, 개인키 ignore 확인
- [x] pip check와 pip-audit 통과
- [x] Ruff, format, Bandit, Django deploy check 통과
- [x] 전체 Git 이력 비밀 패턴 검사
- [x] 저장소 public 전환 및 push
- [x] GitHub Actions 전체 통과
- [x] E2E 화면 아티팩트 다운로드 및 4장 시각 검증

## 이번 요청에서 제외

- [ ] 최종 보고서 원본·PDF 작성
- [ ] 분반·이름·전화번호 뒤 4자리 반영
- [ ] 보고서 전체 페이지 이미지 렌더링과 시각 검증
- [ ] 최종 제출 파일명 확정
