# Deployment Guide

이 문서는 GitHub Actions를 통해 Ubuntu 서버로 자동 배포하는 방법을 설명합니다.

## 배포 아키텍처

```
개발 컴퓨터 (git push) → GitHub → GitHub Actions → Ubuntu 서버
```

## 1. 서버 초기 설정 (한 번만 수행)

### 1.1 Docker 설치

Ubuntu 서버에 SSH로 접속한 후:

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 로그아웃 후 재로그인하여 그룹 변경사항 적용
```

### 1.2 배포 디렉토리 생성

```bash
mkdir -p ~/doctruck_backend
cd ~/doctruck_backend
```

### 1.3 환경 변수 설정

처음 배포 시 `.env.production` 파일을 수동으로 생성해야 합니다:

```bash
cd ~/doctruck_backend

# .env.production 파일 생성
cat > .env.production << 'EOF'
FLASK_ENV=production
FLASK_APP=doctruck_backend.app:create_app

# IMPORTANT: 반드시 변경하세요!
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY

# Database Configuration
DATABASE_URI=sqlite:////db/doctruck_backend.db

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq
CELERY_RESULT_BACKEND_URL=redis://redis
EOF

# SECRET_KEY를 랜덤 값으로 생성
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
# 위 명령의 출력값을 .env.production 파일의 SECRET_KEY에 복사
```

또는:

```bash
nano .env.production  # 파일을 편집기로 열어서 SECRET_KEY 수정
```

## 2. GitHub Secrets 설정

GitHub 저장소에서 배포를 위한 Secret 설정이 필요합니다.

### 2.1 SSH 키 생성 (개발 컴퓨터에서)

```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions

# 공개 키 출력 (서버에 등록할 키)
cat ~/.ssh/github_actions.pub

# 개인 키 출력 (GitHub Secret에 등록할 키)
cat ~/.ssh/github_actions
```

### 2.2 서버에 공개 키 등록

Ubuntu 서버에서:

```bash
# authorized_keys에 공개 키 추가
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys  # 위에서 출력한 공개 키를 붙여넣기
chmod 600 ~/.ssh/authorized_keys
```

### 2.3 GitHub Secrets 등록

GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

다음 Secret들을 등록하세요:

| Secret 이름 | 값 | 설명 |
|------------|-----|------|
| `SERVER_HOST` | `your-server-ip` | 서버 IP 주소 또는 도메인 |
| `SERVER_USER` | `ubuntu` 또는 `your-username` | SSH 접속 사용자명 |
| `SSH_PRIVATE_KEY` | 개인 키 전체 내용 | `~/.ssh/github_actions` 파일의 전체 내용 |
| `SERVER_PORT` | `22` | SSH 포트 (기본값 22) |

## 3. 배포 프로세스

### 3.1 자동 배포

`main` 브랜치에 코드를 푸시하면 자동으로 배포됩니다:

```bash
git add .
git commit -m "feat: new feature"
git push origin main
```

GitHub Actions가 자동으로:
1. 테스트 실행 (lint, pytest)
2. Docker 이미지 빌드
3. 서버로 파일 전송
4. 서버에서 배포 스크립트 실행

### 3.2 수동 배포

GitHub 저장소 → Actions → Deploy to Production Server → Run workflow

### 3.3 배포 확인

서버에서 상태 확인:

```bash
cd ~/doctruck_backend

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# API 테스트
curl http://localhost:5000/api/v1/users
```

## 4. 배포 후 관리

### 4.1 로그 확인

```bash
cd ~/doctruck_backend

# 모든 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f celery
```

### 4.2 서비스 재시작

```bash
cd ~/doctruck_backend

# 모든 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 특정 서비스만 재시작
docker-compose -f docker-compose.prod.yml restart web
```

### 4.3 데이터베이스 백업

```bash
cd ~/doctruck_backend

# SQLite 데이터베이스 백업
cp db/doctruck_backend.db db/doctruck_backend.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 4.4 환경 변수 변경

```bash
cd ~/doctruck_backend

# .env.production 수정
nano .env.production

# 서비스 재시작하여 변경사항 적용
docker-compose -f docker-compose.prod.yml restart
```

### 4.5 더미 데이터 생성 (개발/테스트용)

테스트를 위한 더미 데이터를 자동으로 생성할 수 있습니다.

#### 더미 데이터 생성 (기존 데이터 유지)

```bash
cd ~/doctruck_backend
docker-compose -f docker-compose.prod.yml exec web flask seed
```

#### 기존 데이터 삭제 후 더미 데이터 생성

```bash
cd ~/doctruck_backend
docker-compose -f docker-compose.prod.yml exec web flask seed --clear
```

#### 생성되는 더미 데이터

- **User**: 1개
  - Username: `testuser`
  - Password: `testpass123`
  - Email: `test@test.com`

- **Admin**: 1개
  - Email: `admin@example.com`
  - Password: `admin123`

- **FoodTruck**: 10개 (한식, 중식, 일식, 양식, 디저트, 음료, 분식, 치킨, 피자, 햄버거)
- **Location**: 10개 (여의도 한강공원, 강남역 광장, 홍대 거리 등)
- **Document**: 10개 (다양한 공문서 - 공고/규정/행사)
- **DocumentLocation**: 10개 (문서-위치 연결)
- **FoodTruckLocation**: 10개 (푸드트럭-위치 신청 관계, 다양한 상태)

#### 로그인 테스트

더미 데이터 생성 후 API 테스트:

```bash
# 사용자 로그인 테스트
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# 관리자 로그인 테스트
curl -X POST http://localhost:5000/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

**⚠️ 주의**: `--clear` 옵션은 모든 기존 데이터를 삭제하므로 프로덕션 환경에서 사용 시 주의하세요!

## 5. 트러블슈팅

### 배포 실패 시

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=100

# 컨테이너 완전 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 디스크 공간 정리

```bash
# 사용하지 않는 Docker 이미지 정리
docker system prune -a

# 이전 이미지들 정리
docker image prune -a
```

### 데이터베이스 초기화

**⚠️ 주의: 이 작업은 모든 데이터를 삭제합니다!**

**전제 조건**: 최신 코드가 GitHub Actions를 통해 배포되어 있어야 합니다.

#### 단계별 실행:

```bash
cd ~/doctruck_backend

# 1. 서비스 중지 및 데이터베이스 삭제
docker compose -f docker-compose.prod.yml down
rm -rf db/doctruck_backend.db

# 2. 서비스 재시작 (최신 이미지 사용)
docker compose -f docker-compose.prod.yml up -d

# 3. 서비스 시작 대기
sleep 5

# 4. 데이터베이스 마이그레이션 적용
docker compose -f docker-compose.prod.yml exec web flask db upgrade

# 5-A. 더미 데이터 생성 (개발/테스트용)
docker compose -f docker-compose.prod.yml exec web flask seed --clear

# 5-B. 또는 관리자만 생성 (프로덕션용)
# docker compose -f docker-compose.prod.yml exec web flask init
```

#### 빠른 초기화 (한 줄로 실행):

**개발/테스트 환경 (더미 데이터 포함)**:
```bash
cd ~/doctruck_backend && \
docker compose -f docker-compose.prod.yml down && \
rm -rf db/doctruck_backend.db && \
docker compose -f docker-compose.prod.yml up -d && \
sleep 5 && \
docker compose -f docker-compose.prod.yml exec web flask db upgrade && \
docker compose -f docker-compose.prod.yml exec web flask seed --clear
```

**프로덕션 환경 (관리자만 생성)**:
```bash
cd ~/doctruck_backend && \
docker compose -f docker-compose.prod.yml down && \
rm -rf db/doctruck_backend.db && \
docker compose -f docker-compose.prod.yml up -d && \
sleep 5 && \
docker compose -f docker-compose.prod.yml exec web flask db upgrade && \
docker compose -f docker-compose.prod.yml exec web flask init
```

#### 최신 코드가 배포되지 않은 경우:

1. 로컬에서 코드를 커밋하고 푸시:
   ```bash
   git push origin main
   ```

2. GitHub Actions에서 배포 완료 대기

3. 서버에서 위의 데이터베이스 초기화 명령어 실행

## 6. 보안 고려사항

### 6.1 필수 보안 설정

- [ ] `.env.production`의 `SECRET_KEY`를 랜덤한 값으로 변경
- [ ] RabbitMQ 기본 비밀번호 변경
- [ ] 방화벽 설정 (UFW 등)
- [ ] SSL/TLS 인증서 설정 (Let's Encrypt 등)

### 6.2 방화벽 설정 예시

```bash
# UFW 설치 및 활성화
sudo apt install ufw
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 6.3 SSL 인증서 설정 (선택사항)

Nginx를 사용하는 경우 Let's Encrypt로 무료 SSL 인증서 설정:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 7. 모니터링 (선택사항)

### 7.1 서비스 상태 모니터링

```bash
# 자동 재시작 설정 (systemd)
sudo nano /etc/systemd/system/doctruck.service
```

### 7.2 로그 로테이션

```bash
# logrotate 설정
sudo nano /etc/logrotate.d/doctruck
```

## 참고사항

- 프로덕션 환경에서는 SQLite 대신 PostgreSQL 사용을 권장합니다
- 정기적인 데이터베이스 백업을 설정하세요
- 모니터링 도구 (Prometheus, Grafana 등) 도입을 고려하세요
