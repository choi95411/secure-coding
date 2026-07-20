# Security Checklist

- [x] ORM과 SQLi 문자열 검색 회귀
- [x] autoescape와 Stored/Reflected XSS 테스트
- [x] CSRF middleware 및 상태 변경 POST
- [x] 상품 소유권 IDOR 403 테스트
- [x] Django 비밀번호 해시·강도 검증
- [x] HttpOnly/SameSite, X-Frame-Options, nosniff
- [x] 이미지 확장자·MIME·크기·내용·UUID 경로 검증
- [x] Debug/SSL/HSTS 환경변수 분리
- [ ] 로그인 무차별 대입 제한
- [ ] WebSocket 인증·참여자·Rate Limit
- [ ] 신고 중복·도배와 제재 임계치
- [x] 송금 멱등·롤백·원장 정합성 및 PostgreSQL 전용 동시성 테스트(컨테이너 실행 대기)
- [ ] 관리자 권한·감사 로그 회귀
- [ ] 의존성·Git 이력 비밀 검사

SEC-001: 계정 상태 middleware가 message middleware보다 앞서면 제재 계정 요청에서 메시지 저장소 오류가 날 수 있었다. 순서를 교정했다.

SEC-002: 초기 개발 기본 SECRET_KEY가 배포 검사 기준보다 짧았다. 긴 개발 표식 값과 `.env` 교체 절차, HTTPS/HSTS 환경변수를 추가했다. 운영은 별도 난수 키를 요구한다.
