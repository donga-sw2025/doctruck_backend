# 개발 진행 기록 (Development Log)

이 파일은 FUNCTIONAL_SPECIFICATIONS.md에 명시된 기능들의 개발 진행 상황을 기록합니다.

---

## 개발 계획 개요

### Phase 1: 데이터베이스 모델 설계
- [ ] User 모델 확장 (이름, 전화번호 추가)
- [ ] Admin 모델 생성
- [ ] FoodTruck 모델 생성
- [ ] Location 모델 생성
- [ ] Document 모델 생성
- [ ] DocumentLocation 관계 테이블 생성
- [ ] FoodTruckLocation 관계 테이블 생성

### Phase 2: 인증 시스템 강화
- [ ] 회원가입 API 구현 (이메일 검증, 비밀번호 정책)
- [ ] 로그인 개선
- [ ] Admin 인증 시스템 구현

### Phase 3: 사용자 API - 내 정보 관리
- [ ] 내 정보 조회 API
- [ ] 내 정보 수정 API
- [ ] 회원 탈퇴 API

### Phase 4: 사용자 API - 푸드트럭 관리
- [ ] 내 푸드트럭 목록 조회
- [ ] 푸드트럭 등록
- [ ] 푸드트럭 상세 조회
- [ ] 푸드트럭 수정
- [ ] 푸드트럭 삭제

### Phase 5: 사용자 API - 위치 조회
- [ ] 위치 목록 조회
- [ ] 위치 필터/검색 (반경 검색, 유형, 기간)
- [ ] 위치 상세 조회
- [ ] 위치 관심 등록

### Phase 6: 사용자 API - 공문서 조회
- [ ] 공문서 목록 조회 (VERIFIED만)
- [ ] 공문서 필터/검색
- [ ] 공문서 상세 조회

### Phase 7: 관리자 API - 공문서 관리
- [ ] 검증 대시보드 (PENDING 문서 목록)
- [ ] 검증 처리 (승인/반려)
- [ ] 공문서 수정
- [ ] 공문서-위치 연결
- [ ] 전체 공문서 목록 조회

### Phase 8: 관리자 API - 위치 관리
- [ ] 위치 목록 조회
- [ ] 위치 등록
- [ ] 위치 수정
- [ ] 위치 삭제

### Phase 9: 관리자 API - 사용자 관리
- [ ] 사용자 목록 조회
- [ ] 사용자 상세 조회

### Phase 10: 고급 기능
- [ ] PostGIS 설정 (위치 기반 검색)
- [ ] 맞춤 위치 추천 알고리즘
- [ ] 맞춤 공문서 알림
- [ ] Celery 비동기 작업 (OCR, AI 요약)

---

## 개발 진행 상황

### 2025-11-06

#### Phase 1 완료: 데이터베이스 모델 설계 ✅

**완료 항목:**
- ✅ User 모델 확장 (name, phone_number, created_at 추가)
- ✅ Admin 모델 생성 (관리자 전용 테이블)
- ✅ FoodTruck 모델 생성
- ✅ Location 모델 생성 (LocationType enum 포함)
- ✅ Document 모델 생성 (DocumentType, DocumentStatus enum 포함)
- ✅ DocumentLocation 관계 테이블 생성 (N:M)
- ✅ FoodTruckLocation 관계 테이블 생성 (N:M + ApplicationStatus)
- ✅ 데이터베이스 마이그레이션 생성 및 적용

**생성된 파일:**
- `doctruck_backend/models/user.py` (수정)
- `doctruck_backend/models/admin.py` (신규)
- `doctruck_backend/models/food_truck.py` (신규)
- `doctruck_backend/models/location.py` (신규)
- `doctruck_backend/models/document.py` (신규)
- `doctruck_backend/models/document_location.py` (신규)
- `doctruck_backend/models/food_truck_location.py` (신규)
- `migrations/versions/8657719ef3ff_initial_migration.py` (자동 생성)

**해결한 이슈:**
- ISSUE-001: Flask 3.0 호환성 문제 (`before_app_first_request` → `record_once`)
- ISSUE-002: User 모델 Primary Key 변경으로 인한 FK 오류
- ISSUE-003: Docker migrations 폴더 초기화 문제

**개발 방침 변경:**
- 보안/인증은 최소화 (비밀번호 해싱, 복잡한 토큰 불필요)
- 기능 구현에 집중
- 간단한 인증만 유지 (있으면 편리한 수준)

---

#### Phase 2 완료: 푸드트럭 CRUD API ✅

**완료 항목:**
- ✅ FoodTruck Schema 생성 (Marshmallow)
- ✅ FoodTruck Resource 생성 (CRUD 5개 API)
- ✅ Blueprint에 라우트 등록
- ✅ Swagger 문서 자동 생성 설정

**생성된 API 엔드포인트:**
```
POST   /api/v1/food-trucks           푸드트럭 등록
GET    /api/v1/food-trucks            내 푸드트럭 목록 (페이지네이션)
GET    /api/v1/food-trucks/{id}       푸드트럭 상세 조회
PUT    /api/v1/food-trucks/{id}       푸드트럭 수정
DELETE /api/v1/food-trucks/{id}       푸드트럭 삭제
```

**생성된 파일:**
- `doctruck_backend/api/schemas/food_truck.py` (신규)
- `doctruck_backend/api/resources/food_truck.py` (신규)
- `doctruck_backend/api/views.py` (수정 - 라우트 추가)

**Spring과의 비교:**
- Schema = DTO
- Resource = Controller
- `api.add_resource()` = `@RequestMapping`
- `method_decorators` = `@PreAuthorize`

**다음 단계: Phase 3 - 위치 조회 API**
- 위치 목록 조회
- 위치 상세 조회
- 위치 필터링 (유형, 기간)
**Spring과의 비교:**
- Spring: `@Entity` 어노테이션을 사용하여 엔티티 클래스 정의
- Flask: SQLAlchemy의 `db.Model`을 상속한 클래스 정의

**작업 내용:**
1. `doctruck_backend/models/` 디렉토리에 각 모델 파일 생성
2. 각 모델의 컬럼과 관계 정의
3. 마이그레이션 파일 생성 및 적용

**Spring 코드 예시:**
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long userId;

    @Column(nullable = false, unique = true)
    private String email;

    // getters, setters...
}
```

**Flask 코드 (예상):**
```python
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    # ...
```

---

## 참고사항

### Flask 개발 시 주의사항 (Spring 개발자를 위한 팁)

1. **의존성 주입 (DI)**
   - Spring: 자동 DI (`@Autowired`)
   - Flask: 수동으로 extensions를 import하여 사용

2. **트랜잭션 관리**
   - Spring: `@Transactional` 자동 관리
   - Flask: 명시적으로 `db.session.commit()` 호출 필요

3. **유효성 검사**
   - Spring: `@Valid`, `@NotNull` 등 어노테이션
   - Flask: Marshmallow Schema에서 정의

4. **예외 처리**
   - Spring: `@ControllerAdvice`, `@ExceptionHandler`
   - Flask: `@blueprint.errorhandler()` 또는 전역 error handler

5. **마이그레이션**
   - Spring: Flyway, Liquibase
   - Flask: Flask-Migrate (Alembic 기반)
