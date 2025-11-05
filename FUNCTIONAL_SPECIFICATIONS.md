# 스키마(Schema)

---

## 사용자(User)

| **Column** | **Type (예시)** | **Key** | **Description** |
| --- | --- | --- | --- |
| `user_id` | `BIGINT` | **PK** | 사용자 고유 ID |
| `email` | `VARCHAR(255)` | Unique | 로그인 이메일 |
| `password_hash` | `VARCHAR(255)` |  | 해시된 비밀번호 |
| `name` | `VARCHAR(100)` |  | 사업자명 또는 이름 |
| `phone_number` | `VARCHAR(20)` |  | 연락처 |
| `created_at` | `DATETIME` |  | 계정 생성일 |

## 푸드트럭(FoodTruck)

| **Column** | **Type (예시)** | **Key** | **Description** |
| --- | --- | --- | --- |
| `truck_id` | `BIGINT` | **PK** | 푸드트럭 고유 ID |
| `owner_id` | `BIGINT` | **FK** (Users.user_id) | 소유자 ID |
| `truck_name` | `VARCHAR(100)` |  | 푸드트럭 이름 |
| `business_registration_number` | `VARCHAR(50)` |  | 사업자 등록 번호 |
| `food_category` | `VARCHAR(50)` |  | 음식 카테고리 (예: '디저트', '한식') |
| `operating_region` | `VARCHAR(100)` |  | 주 활동 지역 (예: '서울', '경기') |
| `created_at` | `DATETIME` |  | 정보 등록일 |

## 사업 가능 위치(Location)

| **Column** | **Type (예시)** | **Key** | **Description** |
| --- | --- | --- | --- |
| `location_id` | `BIGINT` | **PK** | 위치 고유 ID |
| `location_name` | `VARCHAR(255)` |  | 위치 이름 (예: '여의도 한강공원') |
| `location_type` | `ENUM` |  | 위치 유형 (예: 'FESTIVAL', 'PARK') |
| `address` | `VARCHAR(255)` |  | 주소 |
| `latitude` | `DECIMAL(9,6)` |  | 위도 (추천 시스템 핵심) |
| `longitude` | `DECIMAL(9,6)` |  | 경도 (추천 시스템 핵심) |
| `start_datetime` | `DATETIME` |  | 행사 시작 일시 (Null 가능) |
| `end_datetime` | `DATETIME` |  | 행사 종료 일시 (Null 가능) |
| `description_summary` | `TEXT` |  | 요약 정보 (기존 '요약') |

## 공문서(Document)

| **Column** | **Type (예시)** | **Key** | **Description** |
| --- | --- | --- | --- |
| `doc_id` | `BIGINT` | **PK** | 문서 고유 ID |
| `title` | `VARCHAR(255)` |  | 문서 제목 |
| `source` | `VARCHAR(100)` |  | 출처 (예: '서울시청') |
| `original_file_path` | `VARCHAR(255)` |  | 원본 파일 경로 (OCR 대상) |
| `ai_summary` | `TEXT` |  | AI 요약본 (기존 '요약') |
| `document_type` | `ENUM` |  | 문서 유형 (예: 'POLICY', 'NOTICE') |
| `status` | `ENUM` |  | 검증 상태 (예: 'PENDING', 'VERIFIED') |
| `verified_by_admin_id` | `BIGINT` | **FK** (Admins.admin_id) | 검증한 관리자 ID (별도 Admin 테이블 필요) |
| `published_at` | `DATE` |  | 공문서 게시일 (기존 '작성일') |
| `expires_at` | `DATE` |  | 공문서 만료일 |

## 문서↔위치 관계(DocumentLocation)

| **Column** | **Type (예시)** | **Key** | **Description** |
| --- | --- | --- | --- |
| `relation_id` | `BIGINT` | **PK** | 관계 고유 ID |
| `doc_id` | `BIGINT` | **FK** (Documents.doc_id) | 관련 문서 ID |
| `location_id` | `BIGINT` | **FK** (BusinessLocations.location_id) | 관련 위치 ID |

## 푸드트럭↔위치 관계(FoodTruckLocation)

| **Column** | **Type (예시)** | **Key** | **Description** |
| --- | --- | --- | --- |
| `application_id` | `BIGINT` | **PK** | 신청/관심 고유 ID |
| `truck_id` | `BIGINT` | **FK** (FoodTrucks.truck_id) | 푸드트럭 ID |
| `location_id` | `BIGINT` | **FK** (BusinessLocations.location_id) | 위치 ID |
| `status` | `ENUM` |  | 상태 (예: 'INTERESTED', 'APPLIED') |

# 기능(Function)

---

## 사용자 기능

| 구분 | 1depth | 2depth | 3depth | 설명 | 예외처리 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| 사용자 인증 | 회원가입 |  |  | 이메일, 비밀번호, 이름(사업자명), 연락처로 회원가입 | - 이메일 형식 오류 - 이메일 중복 - 비밀번호 정책 위반 |  |
|  | 로그인 |  |  | 이메일, 비밀번호로 로그인 (JWT 토큰 발급) | - 이메일/비밀번호 불일치 - 존재하지 않는 계정 |  |
|  | 내 정보 관리 | 조회 |  | 인증 토큰을 기반으로 본인 정보 조회 | - 인증 실패 (토큰 만료/없음) |  |
|  |  | 수정 |  | 이름(사업자명), 연락처 등 수정 | - 인증 실패 |  |
|  |  | 회원 탈퇴 |  | 계정 비활성화/삭제 | - 인증 실패 |  |
| 푸드트럭 | 내 푸드트럭 목록 |  |  | 본인(owner_id)이 소유한 푸드트럭 목록 조회 | - 인증 실패 - 등록된 트럭 없음 (Empty View) |  |
|  |  | 등록 |  | 새 푸드트럭 정보 등록 (truck_name, food_category 등) | - 인증 실패 - 필수 입력값 누락 (카테고리 등) |  |
|  |  | 상세 조회 |  | 특정 truck_id의 상세 정보 조회 | - 인증 실패 - 존재하지 않는 트럭 ID - 본인 소유 트럭이 아닐 경우 (권한 없음) |  |
|  |  |  | 수정 | 트럭 이름, 카테고리, 주 활동 지역 등 수정 | - 인증 실패 - 권한 없음 |  |
|  |  |  | 삭제 | 등록된 푸드트럭 정보 삭제 | - 인증 실패 - 권한 없음 |  |
| 사업 위치 | 위치 목록 조회 |  |  | BusinessLocations 목록 조회 (기본: 전체 목록) | - |  |
|  |  | 필터/검색 |  | (핵심) 위치(위도/경도) 기반 반경 검색, 유형(축제/공원), 기간(날짜) 필터링, 키워드 검색 | - 유효하지 않은 좌표값 - 유효하지 않은 필터값 | API에서 위도/경도 기반 거리 계산 필요 |
|  |  | 상세 조회 |  | 특정 location_id의 상세 정보 조회 (위치, 기간, 요약) | - 존재하지 않는 위치 ID | 관련 공문서(DocumentLocationRelations) 정보 포함 |
|  |  | 관심 등록 |  | 특정 위치에 '관심 있음'(INTERESTED) 등록 (TruckLocationApplications) | - 인증 실패 - 이미 관심 등록됨 - 존재하지 않는 위치 ID | (UI) '어떤 트럭으로' 관심 등록할지 선택 필요 |
| 공문서 | 공문서 목록 조회 |  |  | status = 'VERIFIED'인 공문서 목록 조회 | - | 관리자가 검증한 문서만 노출 |
|  |  | 필터/검색 |  | 유형(document_type), 출처(source), 키워드(제목, 요약) 검색 | - 유효하지 않은 필터값 |  |
|  |  | 상세 조회 |  | 특정 doc_id의 상세 정보 조회 (AI 요약, 출처, 만료일 등) | - 존재하지 않는 문서 ID - status != 'VERIFIED' (접근 불가) | 관련 위치(DocumentLocationRelations) 정보 포함 |
| 추천/알림 | 맞춤 위치 추천 |  |  | (핵심) 내 푸드트럭(food_category, operating_region) 정보를 기반으로 BusinessLocations 추천 | - 인증 실패 - 추천의 근거가 되는 푸드트럭 정보 미등록 | 추천 로직(알고리즘) 정의 필요 |
|  | 맞춤 공문서 알림 |  |  | 내 관심 위치, 활동 지역과 관련된 새 VERIFIED 공문서 알림 | - 인증 실패 | DocumentLocationRelations 기반 매칭 |

## 관리자 기능

| 구분 | 1depth | 2depth | 3depth | 설명 | 예외처리 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| 관리자 인증 | 로그인 |  |  | 관리자 전용 계정으로 로그인 | - 관리자 계정 아님 - 이메일/비밀번호 불일치 | 사용자(사업자) 테이블과 분리 |
| 공문서 관리 | 검증 대시보드 |  |  | AI가 수집한 status = 'PENDING' 공문서 목록 조회 | - 관리자 권한 없음 | (핵심) 기획의 '관리자 검증' 기능 |
|  |  | 검증 처리 |  | PENDING 문서를 '승인'(VERIFIED) 또는 '반려'(REJECTED) 처리 | - 관리자 권한 없음 - 존재하지 않는 문서 ID | verified_by_admin_id에 처리자 ID 기록 |
|  |  |  | (수정) | AI 요약본, 제목 등 관리자가 직접 수정 | - 관리자 권한 없음 |  |
|  |  |  | 공문서-위치 연결 | (핵심) VERIFIED된 공문서를 BusinessLocations와 연결 (DocumentLocationRelations 레코드 생성) | - 관리자 권한 없음 - 존재하지 않는 문서/위치 ID | 이 연결을 통해 사용자에게 맞춤 알림 제공 |
|  | (전체) 공문서 목록 |  |  | status와 관계없이 모든 공문서 목록 조회 (CRUD) | - 관리자 권한 없음 |  |
| 사업 위치 관리 | 사업 위치 목록 |  |  | BusinessLocations 전체 목록 조회 | - 관리자 권한 없음 |  |
|  |  | 등록 |  | 신규 사업 위치(축제, 공원 등) 정보 등록 | - 관리자 권한 없음 - 필수값 누락 (좌표, 이름, 유형) |  |
|  |  | 상세 조회/수정 |  | 기존 사업 위치 정보 수정 | - 관리자 권한 없음 - 존재하지 않는 위치 ID |  |
|  |  | 삭제 |  | 사업 위치 정보 삭제 | - 관리자 권한 없음 |  |
| 사용자 관리 | 사용자 목록 |  |  | 전체 Users (사업자) 목록 조회 | - 관리자 권한 없음 |  |
|  |  | 상세 조회 |  | 특정 사용자 정보, 등록한 푸드트럭 목록 등 조회 | - 관리자 권한 없음 - 존재하지 않는 사용자 ID |  |

# 기술 스택 (Tech Stack)

---

| 구분 (Category) | 기술 스택 (Tool) | MVP에서의 핵심 역할 (Key Benefit) |
| --- | --- | --- |
| 백엔드 프레임워크 | 🐍 Flask | 숙련도 활용: 개발자가 가장 자신 있는 프레임워크를 사용하여 API 서버를 빠르게 개발. |
| 데이터베이스 | 🐘 PostgreSQL (+ PostGIS) | '위치 기반' 검색 구현: PostGIS 확장을 통해 "반경 Xkm 내 사업 위치" 같은 핵심 지리 공간 쿼리를 빠르고 정확하게 처리. |
| DB 연결 (ORM) | 🧪 SQLAlchemy (+ GeoAlchemy2) | DB 모델 정의 및 PostGIS 연동: SQLAlchemy로 DB 스키마를 정의하고, GeoAlchemy2를 통해 Python 코드에서 PostGIS의 위치 데이터 타입(Geometry)을 다룸. |
| API 개발 | 🌐 Flask-RESTful (또는 Flask-Smorest) | API 엔드포인트 구축: FoodTruck, BusinessLocations 등의 리소스(Resource)를 빠르고 규격에 맞게(RESTful) 만듦. |
| 관리자 페이지 | 🧑‍💼 Flask-Admin | '관리자 검증' 기능 구현: AI가 수집한 공문서를 PENDING -> VERIFIED로 변경하는 관리자 전용 웹페이지를 직접 코딩하는 것보다 빠르게 구축. |
| 배포 (앱 서버) | 🦄 Gunicorn | Flask 앱 실행 및 관리: Flask 앱을 실행시키고 워커 프로세스를 관리하는 운영용(Production) 앱 서버. (Nginx와 연동) |
| 비동기 작업 큐 | 🐰 Celery | AI/OCR 처리 예약: 시간이 오래 걸리는 공문서 요약(AI/OCR) 작업을 웹 요청과 분리하여 백그라운드에서 처리. (시스템 안정성 확보) |
| 지리 정보 | 🗺️ 카카오 Map API | 좌표 변환 및 시각화: (예상 역할) 사용자가 입력한 주소를 위도/경도로 변환(Geocoding)하거나, DB의 위치 데이터를 프런트엔드 지도에 표시(시각화)할 때 사용. |