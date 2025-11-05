# API 명세서 (API Specification)

푸드트럭 사업자를 위한 위치 추천 및 공문서 알림 서비스 API

**Base URL**: `http://localhost:5000`
**API Version**: v1
**Swagger UI**: `http://localhost:5000/swagger-ui`

---

## 목차

1. [인증 (Authentication)](#인증-authentication)
2. [사용자 기능](#사용자-기능)
   - [푸드트럭 관리](#푸드트럭-관리)
   - [위치 조회](#위치-조회)
   - [공문서 조회](#공문서-조회)
   - [위치 관심 등록](#위치-관심-등록)
   - [맞춤 추천](#맞춤-추천)
3. [관리자 기능](#관리자-기능)
   - [공문서 관리](#관리자-공문서-관리)
   - [위치 관리](#관리자-위치-관리)
   - [사용자 관리](#관리자-사용자-관리)
   - [문서-위치 연결](#문서-위치-연결)

---

## 인증 (Authentication)

### 1. 사용자 로그인

**Endpoint**: `POST /auth/login`

**설명**: 사용자 인증 정보로 로그인하여 JWT 토큰을 발급받습니다.

**Request Body**:
```json
{
  "username": "myuser",
  "password": "mypassword"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- `400`: 잘못된 요청 (username/password 누락)
- `401`: 인증 실패 (잘못된 credential)

---

### 2. 관리자 로그인

**Endpoint**: `POST /auth/admin/login`

**설명**: 관리자 인증 정보로 로그인하여 관리자 권한 토큰을 발급받습니다.

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "adminpassword"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin_id": 1,
  "name": "관리자"
}
```

**참고**: 발급된 토큰은 `"admin:{admin_id}"` 형식의 identity를 포함하여 관리자 권한을 구분합니다.

---

### 3. 액세스 토큰 갱신

**Endpoint**: `POST /auth/refresh`

**설명**: 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.

**Headers**:
```
Authorization: Bearer <refresh_token>
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 4. 토큰 무효화 (로그아웃)

**액세스 토큰 무효화**: `DELETE /auth/revoke_access`
**리프레시 토큰 무효화**: `DELETE /auth/revoke_refresh`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "token revoked"
}
```

---

## 사용자 기능

**공통 헤더**: 아래 모든 사용자 API는 JWT 토큰이 필요합니다 (명시된 경우 제외).

```
Authorization: Bearer <access_token>
```

---

### 푸드트럭 관리

#### 1. 내 푸드트럭 목록 조회

**Endpoint**: `GET /api/v1/food-trucks`

**설명**: 본인이 소유한 푸드트럭 목록을 조회합니다 (페이지네이션 지원).

**Query Parameters**:
- `page` (optional): 페이지 번호 (기본값: 1)
- `per_page` (optional): 페이지당 개수 (기본값: 10)

**Response** (200 OK):
```json
{
  "total": 5,
  "pages": 1,
  "next": "/api/v1/food-trucks?page=2&per_page=10",
  "prev": "/api/v1/food-trucks?page=1&per_page=10",
  "results": [
    {
      "truck_id": 1,
      "owner_id": 10,
      "truck_name": "맛있는 푸드트럭",
      "business_registration_number": "123-45-67890",
      "food_category": "디저트",
      "operating_region": "서울",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

#### 2. 푸드트럭 등록

**Endpoint**: `POST /api/v1/food-trucks`

**설명**: 새로운 푸드트럭을 등록합니다.

**Request Body**:
```json
{
  "truck_name": "맛있는 푸드트럭",
  "business_registration_number": "123-45-67890",
  "food_category": "디저트",
  "operating_region": "서울"
}
```

**Response** (201 Created):
```json
{
  "message": "푸드트럭이 등록되었습니다.",
  "food_truck": {
    "truck_id": 1,
    "owner_id": 10,
    "truck_name": "맛있는 푸드트럭",
    "business_registration_number": "123-45-67890",
    "food_category": "디저트",
    "operating_region": "서울",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

---

#### 3. 푸드트럭 상세 조회

**Endpoint**: `GET /api/v1/food-trucks/{truck_id}`

**설명**: 특정 푸드트럭의 상세 정보를 조회합니다 (본인 소유만 가능).

**Response** (200 OK):
```json
{
  "food_truck": {
    "truck_id": 1,
    "owner_id": 10,
    "truck_name": "맛있는 푸드트럭",
    "business_registration_number": "123-45-67890",
    "food_category": "디저트",
    "operating_region": "서울",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error Responses**:
- `403`: 권한 없음 (본인 소유 트럭이 아님)
- `404`: 푸드트럭을 찾을 수 없음

---

#### 4. 푸드트럭 수정

**Endpoint**: `PUT /api/v1/food-trucks/{truck_id}`

**설명**: 푸드트럭 정보를 수정합니다 (부분 수정 지원).

**Request Body**:
```json
{
  "truck_name": "새로운 트럭 이름",
  "food_category": "한식",
  "operating_region": "경기"
}
```

**Response** (200 OK):
```json
{
  "message": "푸드트럭이 수정되었습니다.",
  "food_truck": { ... }
}
```

---

#### 5. 푸드트럭 삭제

**Endpoint**: `DELETE /api/v1/food-trucks/{truck_id}`

**설명**: 푸드트럭을 삭제합니다.

**Response** (200 OK):
```json
{
  "message": "푸드트럭이 삭제되었습니다."
}
```

---

### 위치 조회

**참고**: 위치 조회 API는 인증이 필요하지 않습니다 (공개 API).

#### 1. 위치 목록 조회

**Endpoint**: `GET /api/v1/locations`

**설명**: 사업 가능한 위치 목록을 조회합니다 (필터링 및 검색 지원).

**Query Parameters**:
- `location_type` (optional): 위치 유형 (FESTIVAL, PARK, MARKET, STREET, OTHER)
- `start_date` (optional): 운영 시작일 필터 (YYYY-MM-DD)
- `end_date` (optional): 운영 종료일 필터 (YYYY-MM-DD)
- `search` (optional): 검색어 (위치명 또는 주소)
- `page` (optional): 페이지 번호
- `per_page` (optional): 페이지당 개수

**Example Request**:
```
GET /api/v1/locations?location_type=FESTIVAL&start_date=2024-05-01&search=한강
```

**Response** (200 OK):
```json
{
  "total": 15,
  "pages": 2,
  "results": [
    {
      "location_id": 1,
      "location_name": "여의도 한강공원",
      "location_type": "PARK",
      "address": "서울시 영등포구 여의동로 330",
      "latitude": 37.5285,
      "longitude": 126.9335,
      "operating_start_date": "2024-05-01",
      "operating_end_date": "2024-10-31",
      "max_capacity": 20,
      "current_applicants": 5,
      "application_deadline": "2024-04-15",
      "description": "한강공원 푸드트럭 존",
      "contact_info": "02-1234-5678",
      "created_at": "2024-01-10T09:00:00",
      "updated_at": "2024-01-15T14:30:00"
    }
  ]
}
```

---

#### 2. 위치 상세 조회

**Endpoint**: `GET /api/v1/locations/{location_id}`

**설명**: 특정 위치의 상세 정보를 조회합니다.

**Response** (200 OK):
```json
{
  "location": {
    "location_id": 1,
    "location_name": "여의도 한강공원",
    "location_type": "PARK",
    "address": "서울시 영등포구 여의동로 330",
    "latitude": 37.5285,
    "longitude": 126.9335,
    "operating_start_date": "2024-05-01",
    "operating_end_date": "2024-10-31",
    "max_capacity": 20,
    "current_applicants": 5,
    "application_deadline": "2024-04-15",
    "description": "한강공원 푸드트럭 존",
    "contact_info": "02-1234-5678",
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-15T14:30:00"
  }
}
```

---

### 공문서 조회

**참고**: 공문서 조회 API는 인증이 필요하지 않습니다 (공개 API). VERIFIED 상태의 문서만 조회 가능합니다.

#### 1. 공문서 목록 조회

**Endpoint**: `GET /api/v1/documents`

**설명**: VERIFIED 상태의 공문서 목록을 조회합니다 (필터링 및 검색 지원).

**Query Parameters**:
- `document_type` (optional): 문서 유형 (POLICY, NOTICE, REGULATION, EVENT, OTHER)
- `source` (optional): 출처 필터 (예: 서울시청)
- `start_date` (optional): 게시일 시작 필터 (YYYY-MM-DD)
- `end_date` (optional): 게시일 종료 필터 (YYYY-MM-DD)
- `search` (optional): 검색어 (제목 또는 AI 요약)
- `page` (optional): 페이지 번호
- `per_page` (optional): 페이지당 개수

**Example Request**:
```
GET /api/v1/documents?document_type=POLICY&source=서울&search=푸드트럭
```

**Response** (200 OK):
```json
{
  "total": 8,
  "pages": 1,
  "results": [
    {
      "doc_id": 1,
      "title": "2024년 푸드트럭 영업 지원 정책",
      "source": "서울시청",
      "original_file_path": "/files/document_001.pdf",
      "ai_summary": "2024년 푸드트럭 사업자를 위한 영업 지원 정책 안내...",
      "document_type": "POLICY",
      "status": "VERIFIED",
      "verified_by_admin_id": 1,
      "published_at": "2024-01-05",
      "expires_at": "2024-12-31",
      "created_at": "2024-01-01T10:00:00",
      "verified_at": "2024-01-02T15:30:00"
    }
  ]
}
```

---

#### 2. 공문서 상세 조회

**Endpoint**: `GET /api/v1/documents/{doc_id}`

**설명**: 특정 공문서의 상세 정보를 조회합니다 (VERIFIED 문서만 가능).

**Response** (200 OK):
```json
{
  "document": {
    "doc_id": 1,
    "title": "2024년 푸드트럭 영업 지원 정책",
    "source": "서울시청",
    "original_file_path": "/files/document_001.pdf",
    "ai_summary": "2024년 푸드트럭 사업자를 위한 영업 지원 정책 안내...",
    "document_type": "POLICY",
    "status": "VERIFIED",
    "verified_by_admin_id": 1,
    "published_at": "2024-01-05",
    "expires_at": "2024-12-31",
    "created_at": "2024-01-01T10:00:00",
    "verified_at": "2024-01-02T15:30:00"
  }
}
```

**Error Responses**:
- `403`: VERIFIED 문서가 아님 (일반 사용자는 접근 불가)
- `404`: 문서를 찾을 수 없음

---

### 위치 관심 등록

#### 1. 위치 관심 등록

**Endpoint**: `POST /api/v1/locations/{location_id}/interest`

**설명**: 특정 위치에 관심 등록(INTERESTED 상태)을 합니다.

**Request Body**:
```json
{
  "truck_id": 1
}
```

**Response** (201 Created):
```json
{
  "message": "위치 관심 등록이 완료되었습니다.",
  "application_id": 10
}
```

**Error Responses**:
- `400`: 이미 관심 등록됨
- `403`: 본인 소유 트럭이 아님
- `404`: 위치 또는 트럭을 찾을 수 없음

---

#### 2. 위치 관심 취소

**Endpoint**: `DELETE /api/v1/locations/{location_id}/interest`

**설명**: 위치 관심 등록을 취소합니다.

**Query Parameters**:
- `truck_id` (required): 푸드트럭 ID

**Example Request**:
```
DELETE /api/v1/locations/5/interest?truck_id=1
```

**Response** (200 OK):
```json
{
  "message": "위치 관심 등록이 취소되었습니다."
}
```

---

#### 3. 내 관심 위치 목록 조회

**Endpoint**: `GET /api/v1/my/interests`

**설명**: 내가 관심 등록한 위치 목록을 조회합니다.

**Query Parameters**:
- `truck_id` (optional): 특정 푸드트럭의 관심 위치만 조회

**Response** (200 OK):
```json
{
  "interests": [
    {
      "application_id": 10,
      "truck_id": 1,
      "location_id": 5,
      "status": "INTERESTED",
      "created_at": "2024-01-20T10:30:00"
    },
    {
      "application_id": 11,
      "truck_id": 1,
      "location_id": 8,
      "status": "INTERESTED",
      "created_at": "2024-01-21T14:20:00"
    }
  ],
  "count": 2
}
```

---

### 맞춤 추천

#### 1. 맞춤 위치 추천 (핵심 기능)

**Endpoint**: `GET /api/v1/recommendations/locations`

**설명**: 사용자의 푸드트럭 정보를 기반으로 맞춤 위치를 추천합니다.

**Query Parameters**:
- `truck_id` (optional): 특정 푸드트럭 기준 추천
- `limit` (optional): 추천 개수 제한 (기본값: 10)

**추천 알고리즘**:
1. **지역 매칭** (+30점): 푸드트럭 활동 지역과 위치 주소 일치
2. **카테고리 매칭** (+20점): 음식 카테고리에 적합한 위치 유형
   - 디저트 → FESTIVAL
   - 한식 → PARK
   - 분식 → MARKET
3. **운영 임박** (+10점): 30일 이내 시작하는 위치
4. **여유 공간** (+10점): 정원 대비 신청자 적음
5. **기본 점수** (+5점): 모든 위치

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "location": {
        "location_id": 5,
        "location_name": "여의도 벚꽃축제",
        "location_type": "FESTIVAL",
        "address": "서울시 영등포구 여의도동",
        "operating_start_date": "2024-04-05",
        "operating_end_date": "2024-04-15",
        "max_capacity": 30,
        "current_applicants": 10
      },
      "score": 65,
      "reason": "활동 지역(서울) 일치, 디저트 카테고리에 적합한 위치, 10일 후 시작, 잔여 20자리"
    },
    {
      "location": {
        "location_id": 8,
        "location_name": "한강공원 야시장",
        "location_type": "MARKET",
        "address": "서울시 영등포구 여의동로 330"
      },
      "score": 50,
      "reason": "활동 지역(서울) 일치, 잔여 15자리"
    }
  ],
  "count": 2
}
```

**참고**:
- 이미 관심 등록한 위치는 제외됩니다
- 신청 마감된 위치는 제외됩니다

---

#### 2. 맞춤 공문서 알림 (핵심 기능)

**Endpoint**: `GET /api/v1/recommendations/documents`

**설명**: 관심 위치 및 활동 지역을 기반으로 맞춤 공문서를 추천합니다.

**Query Parameters**:
- `days` (optional): 최근 N일 이내 VERIFIED된 문서만 (기본값: 7)

**추천 알고리즘**:
1. 내 관심 위치와 연결된 문서
2. 내 활동 지역과 관련된 문서 (출처 기반)
3. 최근 N일 이내 VERIFIED된 문서 우선

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "document": {
        "doc_id": 15,
        "title": "여의도 벚꽃축제 푸드트럭 참여 안내",
        "source": "서울시청",
        "ai_summary": "2024년 여의도 벚꽃축제 푸드트럭 참여 신청 안내...",
        "document_type": "NOTICE",
        "status": "VERIFIED",
        "published_at": "2024-01-25",
        "verified_at": "2024-01-26T10:00:00"
      },
      "reason": "관심 등록한 위치와 관련됨"
    },
    {
      "document": {
        "doc_id": 18,
        "title": "서울시 푸드트럭 운영 규정 개정안",
        "source": "서울시청",
        "ai_summary": "푸드트럭 운영 규정 일부 개정...",
        "document_type": "REGULATION",
        "status": "VERIFIED",
        "published_at": "2024-01-28"
      },
      "reason": "활동 지역(서울) 관련 문서"
    }
  ],
  "count": 2
}
```

---

## 관리자 기능

**공통 헤더**: 아래 모든 관리자 API는 관리자 JWT 토큰이 필요합니다.

```
Authorization: Bearer <admin_access_token>
```

**참고**: 관리자 토큰은 `/auth/admin/login`에서 발급받습니다.

---

### 관리자 공문서 관리

#### 1. 검증 대기 문서 목록 조회

**Endpoint**: `GET /api/v1/admin/documents/pending`

**설명**: 관리자 검증을 위한 PENDING 상태 문서 목록을 조회합니다.

**Response** (200 OK):
```json
{
  "total": 5,
  "pages": 1,
  "results": [
    {
      "doc_id": 25,
      "title": "AI가 수집한 공문서",
      "source": "부산시청",
      "document_type": "POLICY",
      "status": "PENDING",
      "created_at": "2024-01-30T09:00:00"
    }
  ]
}
```

---

#### 2. 문서 검증 처리 (승인/반려)

**Endpoint**: `PUT /api/v1/admin/documents/{doc_id}/verify`

**설명**: PENDING 문서를 VERIFIED(승인) 또는 REJECTED(반려)로 변경합니다.

**Request Body (승인)**:
```json
{
  "action": "approve"
}
```

**Request Body (반려)**:
```json
{
  "action": "reject",
  "rejection_reason": "내용이 부정확함"
}
```

**Response** (200 OK):
```json
{
  "message": "문서가 승인되었습니다.",
  "document": {
    "doc_id": 25,
    "title": "AI가 수집한 공문서",
    "status": "VERIFIED",
    "verified_by_admin_id": 1,
    "verified_at": "2024-01-30T10:30:00"
  }
}
```

**Error Responses**:
- `400`: PENDING 상태가 아님, action 값 오류, rejection_reason 누락
- `403`: 관리자 권한 없음
- `404`: 문서를 찾을 수 없음

---

#### 3. 전체 문서 목록 조회

**Endpoint**: `GET /api/v1/admin/documents`

**설명**: 상태와 무관하게 모든 문서 목록을 조회합니다.

**Query Parameters**:
- `status` (optional): 상태 필터 (PENDING, VERIFIED, REJECTED)

**Example Request**:
```
GET /api/v1/admin/documents?status=VERIFIED
```

**Response**: 일반 문서 목록과 동일

---

#### 4. 문서 수정

**Endpoint**: `PUT /api/v1/admin/documents/{doc_id}`

**설명**: 문서 정보를 수정합니다.

**Request Body**:
```json
{
  "title": "수정된 제목",
  "ai_summary": "수정된 요약",
  "published_at": "2024-02-01",
  "expires_at": "2024-12-31"
}
```

**Response** (200 OK):
```json
{
  "message": "문서가 수정되었습니다.",
  "document": { ... }
}
```

---

#### 5. 문서 삭제

**Endpoint**: `DELETE /api/v1/admin/documents/{doc_id}`

**설명**: 문서를 삭제합니다.

**Response** (200 OK):
```json
{
  "message": "문서가 삭제되었습니다."
}
```

---

### 관리자 위치 관리

#### 1. 전체 위치 목록 조회

**Endpoint**: `GET /api/v1/admin/locations`

**설명**: 모든 위치 목록을 조회합니다 (페이지네이션 지원).

**Response**: 일반 위치 목록과 동일

---

#### 2. 새 위치 등록

**Endpoint**: `POST /api/v1/admin/locations`

**설명**: 새로운 사업 위치를 등록합니다.

**Request Body**:
```json
{
  "location_name": "여의도 한강공원",
  "location_type": "PARK",
  "address": "서울시 영등포구 여의동로 330",
  "latitude": 37.5285,
  "longitude": 126.9335,
  "operating_start_date": "2024-05-01",
  "operating_end_date": "2024-10-31",
  "max_capacity": 20,
  "application_deadline": "2024-04-15",
  "description": "한강공원 푸드트럭 존",
  "contact_info": "02-1234-5678"
}
```

**Response** (201 Created):
```json
{
  "message": "위치가 등록되었습니다.",
  "location": { ... }
}
```

---

#### 3. 위치 상세 조회

**Endpoint**: `GET /api/v1/admin/locations/{location_id}`

**설명**: 위치 상세 정보를 조회합니다.

**Response**: 일반 위치 상세와 동일

---

#### 4. 위치 수정

**Endpoint**: `PUT /api/v1/admin/locations/{location_id}`

**설명**: 위치 정보를 수정합니다 (부분 수정 지원).

**Request Body**:
```json
{
  "max_capacity": 30,
  "description": "수정된 설명"
}
```

**Response** (200 OK):
```json
{
  "message": "위치가 수정되었습니다.",
  "location": { ... }
}
```

---

#### 5. 위치 삭제

**Endpoint**: `DELETE /api/v1/admin/locations/{location_id}`

**설명**: 위치를 삭제합니다.

**Response** (200 OK):
```json
{
  "message": "위치가 삭제되었습니다."
}
```

---

### 관리자 사용자 관리

#### 1. 전체 사용자 목록 조회

**Endpoint**: `GET /api/v1/admin/users`

**설명**: 모든 사용자 목록을 조회합니다 (페이지네이션 지원).

**Response** (200 OK):
```json
{
  "total": 50,
  "pages": 5,
  "results": [
    {
      "id": 10,
      "username": "user1",
      "email": "user1@example.com",
      "active": true
    }
  ]
}
```

---

#### 2. 사용자 상세 조회

**Endpoint**: `GET /api/v1/admin/users/{user_id}`

**설명**: 사용자 상세 정보와 소유 푸드트럭 목록을 조회합니다.

**Response** (200 OK):
```json
{
  "user": {
    "id": 10,
    "username": "user1",
    "email": "user1@example.com",
    "name": "홍길동",
    "phone_number": "010-1234-5678",
    "active": true,
    "created_at": "2024-01-01T10:00:00"
  },
  "food_trucks": [
    {
      "truck_id": 1,
      "truck_name": "맛있는 푸드트럭",
      "food_category": "디저트",
      "operating_region": "서울"
    }
  ]
}
```

---

### 문서-위치 연결

#### 1. 문서-위치 연결 (핵심 기능)

**Endpoint**: `POST /api/v1/admin/documents/{doc_id}/locations/{location_id}`

**설명**: DocumentLocation 연결을 생성합니다 (사용자 맞춤 알림용).

**Response** (201 Created):
```json
{
  "message": "공문서와 위치가 연결되었습니다.",
  "relation_id": 50
}
```

**Error Responses**:
- `400`: 이미 연결되어 있음
- `404`: 문서 또는 위치를 찾을 수 없음

**참고**: 이 연결을 통해 사용자는 관심 위치와 관련된 공문서 알림을 받을 수 있습니다.

---

#### 2. 문서-위치 연결 해제

**Endpoint**: `DELETE /api/v1/admin/documents/{doc_id}/locations/{location_id}`

**설명**: DocumentLocation 연결을 삭제합니다.

**Response** (200 OK):
```json
{
  "message": "공문서와 위치 연결이 해제되었습니다."
}
```

---

#### 3. 문서에 연결된 위치 목록 조회

**Endpoint**: `GET /api/v1/admin/documents/{doc_id}/locations`

**설명**: 특정 문서에 연결된 위치 목록을 조회합니다.

**Response** (200 OK):
```json
{
  "doc_id": 15,
  "location_ids": [5, 8, 12],
  "count": 3
}
```

---

## 데이터 모델

### LocationType (위치 유형)
- `FESTIVAL`: 축제
- `PARK`: 공원
- `MARKET`: 시장
- `STREET`: 거리
- `OTHER`: 기타

### DocumentType (문서 유형)
- `POLICY`: 정책
- `NOTICE`: 공고
- `REGULATION`: 규정
- `EVENT`: 행사
- `OTHER`: 기타

### DocumentStatus (문서 검증 상태)
- `PENDING`: 검증 대기 (AI가 수집한 상태)
- `VERIFIED`: 검증 완료 (관리자 승인)
- `REJECTED`: 반려 (관리자가 거부)

### ApplicationStatus (신청 상태)
- `INTERESTED`: 관심 있음
- `APPLIED`: 신청 완료
- `APPROVED`: 승인됨
- `REJECTED`: 거절됨
- `CANCELLED`: 취소됨

---

## 에러 코드

| HTTP Status | 설명 |
|------------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 (파라미터 오류, 유효성 검사 실패) |
| 401 | 인증 실패 (토큰 없음, 만료, 잘못된 credential) |
| 403 | 권한 없음 (관리자 권한 필요, 본인 리소스 아님) |
| 404 | 리소스를 찾을 수 없음 |
| 500 | 서버 내부 오류 |

---

## 페이지네이션

모든 목록 조회 API는 페이지네이션을 지원합니다.

**Query Parameters**:
- `page`: 페이지 번호 (기본값: 1)
- `per_page`: 페이지당 개수 (기본값: 10, 최대: 100)

**Response 구조**:
```json
{
  "total": 100,
  "pages": 10,
  "next": "/api/v1/resource?page=2&per_page=10",
  "prev": "/api/v1/resource?page=1&per_page=10",
  "results": [ ... ]
}
```

---

## 사용 예시

### 시나리오 1: 푸드트럭 사업자의 위치 찾기

1. **로그인**
   ```bash
   POST /auth/login
   ```

2. **푸드트럭 등록**
   ```bash
   POST /api/v1/food-trucks
   {
     "truck_name": "디저트 트럭",
     "food_category": "디저트",
     "operating_region": "서울"
   }
   ```

3. **맞춤 위치 추천 받기**
   ```bash
   GET /api/v1/recommendations/locations?truck_id=1
   ```

4. **관심 위치 등록**
   ```bash
   POST /api/v1/locations/5/interest
   {
     "truck_id": 1
   }
   ```

5. **맞춤 공문서 알림 확인**
   ```bash
   GET /api/v1/recommendations/documents
   ```

---

### 시나리오 2: 관리자의 공문서 검증

1. **관리자 로그인**
   ```bash
   POST /auth/admin/login
   ```

2. **검증 대기 문서 조회**
   ```bash
   GET /api/v1/admin/documents/pending
   ```

3. **문서 승인**
   ```bash
   PUT /api/v1/admin/documents/25/verify
   {
     "action": "approve"
   }
   ```

4. **위치 등록**
   ```bash
   POST /api/v1/admin/locations
   {
     "location_name": "벚꽃축제",
     "location_type": "FESTIVAL",
     ...
   }
   ```

5. **문서-위치 연결**
   ```bash
   POST /api/v1/admin/documents/25/locations/5
   ```

---

## 개발 환경 설정

### 로컬 실행

```bash
# Docker Compose로 실행
docker-compose up -d

# 접속
API: http://localhost:5000
Swagger UI: http://localhost:5000/swagger-ui
```

### 데이터베이스

- **개발**: SQLite (`./db/doctruck_backend.db`)
- **운영 권장**: PostgreSQL + PostGIS

### 마이그레이션

```bash
# 마이그레이션 생성
docker-compose exec web flask db migrate -m "설명"

# 마이그레이션 적용
docker-compose exec web flask db upgrade
```

---

## 참고 자료

- **Swagger UI**: `http://localhost:5000/swagger-ui` - 모든 API를 대화형으로 테스트할 수 있습니다
- **OpenAPI Spec**: `http://localhost:5000/swagger.json` - API 명세를 JSON 형식으로 확인할 수 있습니다
- **FUNCTIONAL_SPECIFICATIONS.md**: 전체 기능 명세
- **DEVELOPMENT_LOG.md**: 개발 진행 기록
- **RUNTIME_ENVIRONMENT.md**: 실행 환경 정보

---

**문서 버전**: 1.0
**마지막 업데이트**: 2024-01-30
