# 이슈 로그 (Issue Log)

이 파일은 개발 중 발생한 문제와 해결 방법을 기록합니다.

---

## [ISSUE-001] Flask 3.0 호환성 문제 - `before_app_first_request` 제거됨

**발생 일시:** 2025-11-06

**증상:**
```
AttributeError: 'Blueprint' object has no attribute 'before_app_first_request'
```

**원인:**
- Flask 3.0에서 `@blueprint.before_app_first_request` 데코레이터가 제거됨
- 기존 코드가 Flask 2.x 기준으로 작성되어 있음

**해결 방법:**
`before_app_first_request`를 `record_once`로 변경

**변경 전:**
```python
@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=login, app=current_app)
```

**변경 후:**
```python
@blueprint.record_once
def register_views(state):
    app_instance = state.app
    apispec.spec.path(view=login, app=app_instance)
```

**영향받은 파일:**
- `doctruck_backend/api/views.py`
- `doctruck_backend/auth/views.py`

**상태:** ✅ 해결됨

---

## [ISSUE-002] User 모델 Primary Key 변경으로 인한 Foreign Key 오류

**발생 일시:** 2025-11-06

**증상:**
```
sqlalchemy.exc.NoForeignKeysError: Could not determine join condition between parent/child tables on relationship TokenBlocklist.user - there are no foreign keys linking these tables.
```

**원인:**
- User 모델의 primary key를 `id`에서 `user_id`로 변경
- User 모델의 테이블명을 `user`에서 `users`로 변경
- 기존 TokenBlocklist 모델이 `user.id`를 참조하고 있었음

**해결 방법:**
하위 호환성을 위해 User 모델을 원래대로 유지
- Primary Key: `id` (Integer) 유지
- 테이블명: `user` 유지
- 새로운 컬럼만 추가 (name, phone_number, created_at)

**변경 사항:**
```python
class User(db.Model):
    __tablename__ = "user"  # 기존 유지
    id = db.Column(db.Integer, primary_key=True)  # 기존 유지
    # 새 컬럼 추가
    name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
```

**영향받은 파일:**
- `doctruck_backend/models/user.py`
- `doctruck_backend/models/food_truck.py` (owner_id FK 수정)

**상태:** ✅ 해결됨

**교훈:** 기존 시스템과의 호환성을 먼저 확인하고, 점진적으로 변경해야 함

---

## [ISSUE-003] Docker migrations 폴더 초기화 문제

**발생 일시:** 2025-11-06

**증상:**
```
Error: Directory migrations already exists and is not empty
```

**원인:**
1. Dockerfile에서 `COPY migrations migrations/`로 로컬 migrations를 컨테이너에 복사
2. docker-compose.yml에서 볼륨 마운트로 로컬 폴더를 컨테이너에 동기화
3. `flask db init`은 빈 폴더가 아니면 실행 거부
4. 로컬에서 삭제해도 Docker 이미지 레이어에 남아있음

**진행 중인 해결 시도:**
1. ❌ 로컬에서 `rm -rf migrations` → 실패 (볼륨 마운트 때문)
2. ❌ 컨테이너 내에서 삭제 시도 → 반복됨

**해결 방법 (미적용):**

### 방법 A: Dockerfile 수정 (권장)
Dockerfile의 `COPY migrations migrations/` 라인 제거 또는 조건부 복사

```dockerfile
# COPY migrations migrations/  # 이 라인 제거
```

### 방법 B: .dockerignore 사용
`.dockerignore` 파일에 migrations 추가
```
migrations/
```

### 방법 C: 초기화 스크립트 사용
```bash
# 컨테이너 완전 재시작
docker-compose down -v  # 볼륨도 삭제
rm -rf migrations
mkdir migrations
docker-compose build
docker-compose up -d
docker-compose exec web flask db init
```

**최종 해결 방법:**
Dockerfile 수정 + 볼륨 완전 삭제

1. Dockerfile에서 `COPY migrations migrations/` 라인 주석 처리
2. `docker-compose down -v` (볼륨까지 완전 삭제)
3. `rm -rf migrations` (로컬 삭제)
4. `docker-compose build && docker-compose up -d`
5. `docker-compose exec web flask db init` (성공)
6. `docker-compose exec web flask db migrate` (마이그레이션 파일 생성)
7. `docker-compose exec web flask db upgrade` (DB에 적용)

**상태:** ✅ 해결됨 (2025-11-06)

**참고사항:**
- Flask-Migrate는 migrations 폴더가 비어있어야 `flask db init` 실행 가능
- Docker 볼륨 마운트와 이미지 레이어 캐싱을 모두 고려해야 함

---

## 템플릿 (새 이슈 기록 시 사용)

```markdown
## [ISSUE-XXX] 이슈 제목

**발생 일시:** YYYY-MM-DD

**증상:**
에러 메시지나 문제 상황 설명

**원인:**
문제가 발생한 근본 원인

**해결 방법:**
실제로 적용한 해결 방법

**영향받은 파일:**
- 파일 경로 1
- 파일 경로 2

**상태:** ✅ 해결됨 / 🔴 진행 중 / ⏸️ 보류

**교훈/참고사항:**
향후 참고할 내용
```

---

## 이슈 통계

- 총 이슈: 3개
- 해결됨: 3개 (100%)
- 진행 중: 0개
- 보류: 0개
