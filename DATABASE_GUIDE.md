# 데이터베이스 가이드

이 문서는 프로젝트에서 사용하는 데이터베이스의 종류와 조회 방법을 설명합니다.

## 📦 사용 중인 데이터베이스

### 개발 환경 (로컬)
- **DB 종류**: SQLite
- **위치**: `db/doctruck_backend.db`
- **설정 파일**: `.flaskenv`
- **연결 문자열**: `sqlite:///doctruck_backend.db`

### 프로덕션 환경 (서버)
- **DB 종류**: SQLite (향후 PostgreSQL 권장)
- **위치**: 서버의 `~/doctruck_backend/db/doctruck_backend.db`
- **설정 파일**: `.env.production`
- **연결 문자열**: `sqlite:////db/doctruck_backend.db`

### SQLite란?
- 파일 기반의 경량 데이터베이스
- 별도의 서버 프로세스가 필요 없음
- 하나의 `.db` 파일에 모든 데이터 저장
- 소규모 애플리케이션에 적합
- **장점**: 설치/설정 불필요, 빠른 개발
- **단점**: 동시 접속 처리 제한적, 대용량 데이터 부적합

---

## 🔍 데이터베이스 조회 방법

### 방법 1: Python으로 조회 (추천)

#### 모든 테이블 목록 보기
```bash
python -c "
import sqlite3
conn = sqlite3.connect('db/doctruck_backend.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;\")
for table in cursor.fetchall():
    print(table[0])
conn.close()
"
```

#### 특정 테이블 데이터 조회
```bash
# User 테이블 조회
python -c "
import sqlite3
conn = sqlite3.connect('db/doctruck_backend.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM user;')
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
"
```

#### 포맷팅된 조회 (컬럼명 포함)
```bash
python -c "
import sqlite3
conn = sqlite3.connect('db/doctruck_backend.db')
cursor = conn.cursor()

# 테이블 스키마 확인
cursor.execute('PRAGMA table_info(user);')
columns = [col[1] for col in cursor.fetchall()]
print('Columns:', ', '.join(columns))
print('-' * 80)

# 데이터 조회
cursor.execute('SELECT id, username, email, active, name FROM user;')
for row in cursor.fetchall():
    print(dict(zip(columns, row)))

conn.close()
"
```

### 방법 2: Docker 컨테이너에서 조회

#### 로컬 개발 환경
```bash
# 컨테이너 내부로 들어가기
docker-compose exec web bash

# Python으로 DB 조회
python -c "
import sqlite3
conn = sqlite3.connect('/db/doctruck_backend.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM user;')
for row in cursor.fetchall():
    print(row)
"
```

#### 프로덕션 서버
```bash
# SSH로 서버 접속 후
cd ~/doctruck_backend

# 컨테이너 내부로 들어가기
docker compose -f docker-compose.prod.yml exec web bash

# Python으로 DB 조회
python -c "
import sqlite3
conn = sqlite3.connect('/db/doctruck_backend.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM user;')
for row in cursor.fetchall():
    print(row)
"
```

### 방법 3: Flask Shell 사용 (ORM 방식)

#### 로컬에서
```bash
# Flask shell 시작
docker-compose exec web flask shell

# 또는 로컬에 Flask가 설치되어 있다면
flask shell
```

#### Flask Shell에서 쿼리
```python
# User 모델 import
from doctruck_backend.models import User, Admin, FoodTruck, Location, Document

# 모든 사용자 조회
users = User.query.all()
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

# 특정 사용자 조회
user = User.query.filter_by(username='testuser').first()
print(user.username, user.email)

# 카운트
user_count = User.query.count()
print(f"Total users: {user_count}")

# 관리자 조회
admins = Admin.query.all()
for admin in admins:
    print(f"ID: {admin.admin_id}, Email: {admin.email}")

# 푸드트럭 조회
trucks = FoodTruck.query.limit(5).all()
for truck in trucks:
    print(f"ID: {truck.truck_id}, Name: {truck.truck_name}, Owner: {truck.owner_id}")

# 조인 쿼리 (푸드트럭과 소유자)
from doctruck_backend.extensions import db
results = db.session.query(FoodTruck, User).join(User, FoodTruck.owner_id == User.id).all()
for truck, owner in results:
    print(f"Truck: {truck.truck_name}, Owner: {owner.username}")
```

### 방법 4: SQLite CLI 도구 (sqlite3 설치 필요)

#### Windows에서 sqlite3 설치
1. https://www.sqlite.org/download.html 에서 다운로드
2. `sqlite-tools-win32-x86-*.zip` 다운로드
3. 압축 해제 후 PATH에 추가

#### 사용법
```bash
# DB 파일 열기
sqlite3 db/doctruck_backend.db

# SQLite 프롬프트에서
.tables                          # 모든 테이블 보기
.schema user                     # user 테이블 스키마 보기
SELECT * FROM user;              # 데이터 조회
.mode column                     # 컬럼 모드로 출력
.headers on                      # 헤더 표시
SELECT id, username, email FROM user;
.quit                            # 종료
```

---

## 📊 자주 사용하는 쿼리 예제

### 1. 사용자 정보 확인
```sql
SELECT id, username, email, active, name, phone_number FROM user;
```

### 2. 관리자 정보 확인
```sql
SELECT admin_id, email, name, active FROM admins;
```

### 3. 푸드트럭 목록 (소유자 정보 포함)
```sql
SELECT
    ft.truck_id,
    ft.truck_name,
    ft.food_category,
    u.username as owner_name,
    u.email as owner_email
FROM food_trucks ft
JOIN user u ON ft.owner_id = u.id;
```

### 4. 위치별 푸드트럭 신청 현황
```sql
SELECT
    l.location_name,
    ft.truck_name,
    ftl.status,
    ftl.created_at
FROM food_truck_locations ftl
JOIN locations l ON ftl.location_id = l.location_id
JOIN food_trucks ft ON ftl.truck_id = ft.truck_id
ORDER BY ftl.created_at DESC;
```

### 5. 문서와 연결된 위치 조회
```sql
SELECT
    d.title as document_title,
    l.location_name,
    d.document_type,
    d.status
FROM document_locations dl
JOIN documents d ON dl.doc_id = d.doc_id
JOIN locations l ON dl.location_id = l.location_id;
```

### 6. 테이블별 레코드 수
```sql
SELECT 'users' as table_name, COUNT(*) as count FROM user
UNION ALL
SELECT 'admins', COUNT(*) FROM admins
UNION ALL
SELECT 'food_trucks', COUNT(*) FROM food_trucks
UNION ALL
SELECT 'locations', COUNT(*) FROM locations
UNION ALL
SELECT 'documents', COUNT(*) FROM documents;
```

---

## 🛠️ 편리한 조회 스크립트

프로젝트 루트에 `scripts/db_query.py` 파일을 만들어 사용하세요:

```python
#!/usr/bin/env python
"""데이터베이스 조회 헬퍼 스크립트"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "doctruck_backend.db"

def query_db(query, params=None):
    """SQL 쿼리 실행"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return rows

def show_tables():
    """모든 테이블 목록"""
    rows = query_db("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    print("\n=== TABLES ===")
    for row in rows:
        print(f"  - {row['name']}")

def show_users():
    """사용자 목록"""
    rows = query_db("SELECT id, username, email, active, name FROM user;")
    print("\n=== USERS ===")
    for row in rows:
        print(f"ID: {row['id']}, Username: {row['username']}, Email: {row['email']}, Active: {row['active']}")

def show_admins():
    """관리자 목록"""
    rows = query_db("SELECT admin_id, email, name, active FROM admins;")
    print("\n=== ADMINS ===")
    for row in rows:
        print(f"ID: {row['admin_id']}, Email: {row['email']}, Name: {row['name']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/db_query.py [tables|users|admins]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "tables":
        show_tables()
    elif command == "users":
        show_users()
    elif command == "admins":
        show_admins()
    else:
        print(f"Unknown command: {command}")
```

사용 예:
```bash
python scripts/db_query.py tables
python scripts/db_query.py users
python scripts/db_query.py admins
```

---

## 🚨 주의사항

### 1. DB 파일 직접 수정 금지
- SQLite 파일을 직접 편집하면 손상될 수 있음
- 항상 SQL 쿼리나 ORM을 통해 수정

### 2. 프로덕션 DB 백업
```bash
# 서버에서 DB 백업
cd ~/doctruck_backend
cp db/doctruck_backend.db db/backup_$(date +%Y%m%d_%H%M%S).db
```

### 3. 동시 접속 주의
- SQLite는 동시 쓰기 제한적
- 여러 프로세스에서 동시에 쓰기 작업 시 락 발생 가능

### 4. 프로덕션에서는 PostgreSQL 권장
SQLite는 개발/테스트용으로 적합하며, 프로덕션에서는 PostgreSQL 사용을 권장합니다.

---

## 📚 추가 자료

- SQLite 공식 문서: https://www.sqlite.org/docs.html
- SQLAlchemy ORM 문서: https://docs.sqlalchemy.org/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
