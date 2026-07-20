# Database Design

- `User`: 고유 username, Django password hash, active/dormant/blocked 인덱스 상태. 삭제 대신 상태 변경.
- `UserProfile`: User와 1:1, 표시 이름·소개.
- `Product`: seller `PROTECT`, 공개 범위와 판매/차단/삭제 상태 분리, 가격 비음수 제약, 공개 최신/판매자 상태 인덱스.
- `ProductImage`: Product 종속, UUID 저장 경로, 검증된 이미지.
- `Conversation`: global/direct 유형, 전체 채팅 조건부 단일 제약, 정렬된 두 사용자 ID의 고유 `direct_key`, 활성 상태.
- `ConversationMember`: 대화/사용자 고유 제약과 사용자별 조회 인덱스.
- `Message`: 대화·발신자 `PROTECT`, 1000자 내용, visible/hidden/deleted 상태, 대화 최근 메시지와 발신자 Rate Limit 인덱스.
- `Report`, `ModerationAction`, `AdminAuditLog`: 중복 방지와 관리자·사유·전후 JSON 보존. 감사 기록은 수정·삭제하지 않는다.
- `Wallet`, `Transfer`, `LedgerEntry`: 사용자별 고유 지갑, 고유 멱등 키, debit/credit 불변 원장. 잔액 변경은 행 잠금 서비스와 조정 거래만 허용한다.
- `LoginThrottle`: username/IP HMAC의 고유 키, 실패 수·창 시작·잠금 종료. 성공 시 삭제하며 원문 식별정보는 저장하지 않는다.

사용자·상품은 상태 변경과 복구를 지원한다. 원장·송금·감사·메시지 발신자 관계는 감사 가능성을 위해 `PROTECT`를 우선한다.
