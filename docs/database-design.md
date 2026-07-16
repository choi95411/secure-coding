# Database Design

- `User`: 고유 username, Django password hash, active/dormant/blocked 인덱스 상태. 삭제 대신 상태 변경.
- `UserProfile`: User와 1:1, 표시 이름·소개, 사용자 삭제 시 함께 삭제.
- `Product`: seller `PROTECT`, 공개 범위와 판매/차단/삭제 상태 분리, 가격 비음수 제약, 공개 최신/판매자 상태 인덱스.
- `ProductImage`: Product에 종속, UUID 저장 경로, 상품 삭제 시 함께 삭제.

후속 `Conversation`, `ConversationMember`, `Message`는 유형·참여자·시간 제약을 둔다. `Report`, `ModerationAction`, `AdminAuditLog`는 중복 방지와 관리자·사유·전후 JSON을 보존한다. `Wallet`, `Transfer`, `LedgerEntry`는 사용자별 고유 지갑, 고유 멱등 키, debit/credit 불변 원장을 사용한다. 잔액 변경은 행 잠금 서비스와 조정 거래만 허용한다.
