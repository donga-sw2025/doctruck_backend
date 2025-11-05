#!/bin/bash
set -e

echo "========================================="
echo "Starting deployment process..."
echo "========================================="

# 환경 변수 파일 확인
if [ ! -f .env.production ]; then
    echo "⚠️  .env.production not found. Creating from example..."
    cp .env.production.example .env.production
    echo "⚠️  Please edit .env.production with proper values!"
    echo "⚠️  Especially change SECRET_KEY to a random value"
fi

# 이전 컨테이너 중지 및 제거
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# 새 컨테이너 시작
echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

# 컨테이너가 준비될 때까지 대기
echo "Waiting for services to be ready..."
sleep 10

# 데이터베이스 마이그레이션
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web flask db upgrade || true

# 초기 데이터 생성 (admin 사용자 등)
echo "Initializing database..."
docker-compose -f docker-compose.prod.yml exec -T web flask init || echo "Already initialized"

# 헬스 체크
echo "Checking service health..."
sleep 5

if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    echo ""
    echo "Services status:"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
else
    echo "❌ Deployment failed!"
    echo "Logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

echo "========================================="
echo "Deployment completed!"
echo "========================================="
