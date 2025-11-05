# 실행 환경 정보 (Runtime Environment)

현재 로컬에서 실행 중인 모든 것들을 정리한 문서입니다.

---

## 🐳 Docker 컨테이너 (4개 실행 중)

### 1. **web** - Flask 애플리케이션 서버
```
이미지: doctruck_backend (직접 빌드)
포트: 0.0.0.0:5000 → 5000
명령어: gunicorn -b 0.0.0.0:5000 doctruck_backend.wsgi:app
```

**역할:**
- Flask 애플리케이션 실행
- API 엔드포인트 제공 (`/api/v1/...`, `/auth/...`)
- Swagger UI 제공 (`/swagger-ui`)

**접속 방법:**
- API: http://localhost:5000/api/v1/food-trucks
- Swagger UI: http://localhost:5000/swagger-ui
- 로그인: http://localhost:5000/auth/login

**Spring Boot와 비교:**
- Spring Boot: 내장 Tomcat으로 실행
- Flask: Gunicorn (WSGI 서버)로 실행

---

### 2. **rabbitmq** - 메시지 브로커
```
이미지: rabbitmq (공식 이미지)
포트: 4369, 5671-5672, 15691-15692, 25672 (내부만)
```

**역할:**
- Celery의 메시지 큐 (Task Queue)
- 비동기 작업 (AI/OCR 등)을 위한 브로커

**현재 상태:**
- 실행 중이지만 아직 Celery 태스크는 구현 안 함
- Phase 10에서 사용 예정

**Spring Boot와 비교:**
- Spring: RabbitMQ 또는 Kafka
- 동일한 역할

---

### 3. **redis** - 캐시/세션 저장소
```
이미지: redis (공식 이미지)
포트: 6379 (내부만)
```

**역할:**
- Celery의 결과 저장소 (Result Backend)
- 향후 캐싱 용도로도 사용 가능

**현재 상태:**
- 실행 중이지만 아직 본격적으로 사용 안 함
- Celery 태스크 구현 시 사용 예정

**Spring Boot와 비교:**
- Spring: Redis 또는 Memcached
- 동일한 역할

---

### 4. **celery** - 비동기 작업 워커 (현재 미실행)
```
상태: 종료됨 (정상)
명령어: celery worker -A doctruck_backend.celery_app:app
```

**역할:**
- 백그라운드 작업 처리 (OCR, AI 요약 등)

**현재 상태:**
- 아직 비동기 태스크 구현 전이라 실행 안 함
- Phase 10에서 구현 예정

**Spring Boot와 비교:**
- Spring: @Async 또는 Spring Batch
- 비슷한 역할이지만 Celery가 더 강력

---

## 📁 Docker 볼륨 마운트

### 로컬 → 컨테이너 연결

```yaml
volumes:
  - ./doctruck_backend:/code/doctruck_backend    # 코드 실시간 반영
  - ./db/:/db/                                     # SQLite DB 저장
```

**의미:**
- 로컬에서 코드 수정 → Docker 컨테이너에 즉시 반영
- 단, Python 파일 수정 시 재시작 필요 (Gunicorn은 auto-reload 안 함)

---

## 🗄️ 데이터베이스

### SQLite (개발용)
```
위치: ./db/doctruck_backend.db
타입: SQLite (파일 기반)
```

**테이블 목록:**
- admins
- user
- food_trucks
- locations
- documents
- document_locations
- food_truck_locations
- token_blocklist

**Spring Boot와 비교:**
- Spring: application.yml에 DataSource 설정
- Flask: config.py에 DATABASE_URI 설정

**운영 환경에서는:**
- PostgreSQL + PostGIS로 전환 예정 (위치 기반 검색용)

---

## 🔧 실행 중인 프로세스 정리

| 프로세스 | 위치 | 포트 | 역할 |
|---------|------|------|------|
| **Gunicorn** | Docker (web) | 5000 | Flask 앱 실행 |
| **RabbitMQ** | Docker | 내부 | 메시지 큐 |
| **Redis** | Docker | 내부 | 캐시/결과 저장 |

---

## 🌐 접속 가능한 URL

```
✅ API Base URL:
   http://localhost:5000/api/v1

✅ Swagger UI (API 문서 + 테스트):
   http://localhost:5000/swagger-ui

✅ ReDoc UI (API 문서):
   http://localhost:5000/redoc-ui

✅ OpenAPI Spec (JSON):
   http://localhost:5000/swagger.json

✅ 인증 엔드포인트:
   http://localhost:5000/auth/login
   http://localhost:5000/auth/refresh
```

---

## 💻 로컬 환경 (Windows)

### Python 환경
```
Python: 3.8 (Docker 내부)
가상환경: 사용 안 함 (Docker 사용 중)
```

### 로컬 파일
```
C:\Users\pupaj\projects\doctruck_backend\doctruck_backend\
├── doctruck_backend/          # 소스 코드
│   ├── models/                # 데이터베이스 모델
│   ├── api/                   # API 엔드포인트
│   ├── auth/                  # 인증
│   └── ...
├── migrations/                # DB 마이그레이션 파일
├── db/                        # SQLite DB 파일
├── docker-compose.yml         # Docker 설정
└── Dockerfile                 # Docker 이미지 빌드
```

---

## 🔄 코드 변경 시 반영 방법

### Python 코드 수정 시
```bash
# 1. 코드 수정
# 2. Docker 컨테이너 재시작
docker-compose restart web

# 또는 재빌드 (모델 변경 등)
docker-compose down
docker-compose build web
docker-compose up -d
```

### 데이터베이스 모델 변경 시
```bash
# 1. 모델 수정
# 2. 마이그레이션 생성
docker-compose exec web flask db migrate -m "변경 내용"

# 3. 마이그레이션 적용
docker-compose exec web flask db upgrade
```

---

## 🛑 전체 중지 방법

```bash
# 모든 컨테이너 중지
docker-compose down

# 컨테이너 + 볼륨까지 삭제
docker-compose down -v
```

---

## 📊 리소스 사용량

```bash
# Docker 컨테이너 리소스 확인
docker stats

# 컨테이너별 로그 확인
docker-compose logs web
docker-compose logs rabbitmq
docker-compose logs redis
```

---

## 🔍 디버깅

### 컨테이너 내부 접속
```bash
# web 컨테이너 내부로 들어가기
docker-compose exec web bash

# Python 인터프리터 실행
docker-compose exec web python

# Flask shell 실행
docker-compose exec web flask shell
```

---

## Spring Boot와의 전체 비교

| 항목 | Spring Boot | Flask (현재 환경) |
|------|------------|------------------|
| **애플리케이션 서버** | 내장 Tomcat | Gunicorn |
| **실행 방법** | `java -jar app.jar` | `gunicorn wsgi:app` |
| **개발 서버** | `./mvnw spring-boot:run` | `flask run` |
| **핫 리로드** | Spring DevTools | Flask debug mode |
| **포트** | 8080 (기본) | 5000 (기본) |
| **DB 마이그레이션** | Flyway/Liquibase | Flask-Migrate |
| **비동기 작업** | @Async | Celery |
| **API 문서** | Swagger/SpringDoc | APISpec (Swagger) |
| **설정 파일** | application.yml | config.py + .flaskenv |

---

## 요약

**현재 실행 중:**
1. ✅ Flask 웹 서버 (http://localhost:5000)
2. ✅ RabbitMQ (메시지 큐 - 향후 사용)
3. ✅ Redis (캐시 - 향후 사용)
4. ✅ SQLite DB (데이터 저장)

**실행 환경:**
- Docker 컨테이너 4개
- Windows 로컬 개발 환경
- 코드는 로컬 → Docker에 마운트되어 실시간 동기화
