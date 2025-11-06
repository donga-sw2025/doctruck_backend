"""Seed dummy data for development and testing"""

import random
from datetime import datetime, timedelta
from decimal import Decimal

import click
from flask.cli import with_appcontext

from doctruck_backend.extensions import db
from doctruck_backend.models import (
    User,
    Admin,
    FoodTruck,
    Location,
    LocationType,
    Document,
    DocumentType,
    DocumentStatus,
    DocumentLocation,
    FoodTruckLocation,
    ApplicationStatus,
)


def random_date(start_days_ago=30, end_days_ahead=60):
    """Generate random datetime"""
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() + timedelta(days=end_days_ahead)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def random_coordinate(base_lat=37.5665, base_lon=126.9780, range_km=50):
    """Generate random coordinates around Seoul
    1 degree latitude ≈ 111km
    1 degree longitude ≈ 88km (at 37° latitude)
    """
    lat_offset = (random.random() - 0.5) * (range_km / 111) * 2
    lon_offset = (random.random() - 0.5) * (range_km / 88) * 2
    return (
        Decimal(str(round(base_lat + lat_offset, 6))),
        Decimal(str(round(base_lon + lon_offset, 6))),
    )


@click.command("seed")
@click.option("--clear", is_flag=True, help="Clear existing data before seeding")
@with_appcontext
def seed_dummy_data(clear):
    """Create dummy data for all models (10 each, except User/Admin)"""

    if clear:
        click.echo("Clearing existing data...")
        try:
            FoodTruckLocation.query.delete()
            DocumentLocation.query.delete()
            Document.query.delete()
            FoodTruck.query.delete()
            Location.query.delete()
            Admin.query.delete()
            User.query.delete()
            db.session.commit()
            click.echo("Existing data cleared!")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Note: Could not clear data (tables may not exist yet): {e}")
            click.echo("Continuing with seeding...")

    # 1. Create 1 User and 1 Admin
    click.echo("Creating User and Admin...")

    user = User.query.filter_by(username="testuser").first()
    if not user:
        user = User(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            active=True,
            name="테스트 사용자",
            phone_number="010-1234-5678",
        )
        db.session.add(user)
        click.echo("  - Created user: testuser")
    else:
        # 기존 사용자의 패스워드를 업데이트 (clear 옵션 사용 시 일관성 보장)
        user.password = "testpass123"
        user.email = "test@test.com"
        user.active = True
        user.name = "테스트 사용자"
        user.phone_number = "010-1234-5678"
        click.echo("  - User testuser already exists, updated password")

    admin = Admin.query.filter_by(email="admin@example.com").first()
    if not admin:
        admin = Admin(
            email="admin@example.com",
            password="admin123",
            name="관리자",
            active=True,
        )
        db.session.add(admin)
        click.echo("  - Created admin: admin@example.com")
    else:
        # 기존 관리자의 패스워드를 업데이트 (clear 옵션 사용 시 일관성 보장)
        admin.password = "admin123"
        admin.name = "관리자"
        admin.active = True
        click.echo("  - Admin already exists, updated password")

    db.session.commit()

    # 2. Create 10 FoodTrucks
    click.echo("\nCreating 10 Food Trucks...")
    food_categories = [
        "한식",
        "중식",
        "일식",
        "양식",
        "디저트",
        "음료",
        "분식",
        "치킨",
        "피자",
        "햄버거",
    ]
    regions = ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산"]

    food_trucks = []
    for i in range(10):
        truck = FoodTruck(
            owner_id=user.id,
            truck_name=f"{food_categories[i]} 푸드트럭 {i+1}",
            business_registration_number=f"123-45-{60000+i:05d}",
            food_category=food_categories[i],
            operating_region=random.choice(regions),
        )
        db.session.add(truck)
        food_trucks.append(truck)
        click.echo(f"  - Created: {truck.truck_name}")

    db.session.commit()

    # 3. Create 10 Locations
    click.echo("\nCreating 10 Locations...")
    location_types = list(LocationType)
    location_names = [
        "여의도 한강공원",
        "강남역 광장",
        "홍대 거리",
        "DDP 광장",
        "북촌 한옥마을",
        "서울숲",
        "남산 타워 입구",
        "이태원 거리",
        "광화문 광장",
        "잠실 종합운동장",
    ]
    addresses = [
        "서울 영등포구 여의동로",
        "서울 강남구 강남대로",
        "서울 마포구 양화로",
        "서울 중구 을지로",
        "서울 종로구 계동길",
        "서울 성동구 뚝섬로",
        "서울 용산구 남산공원길",
        "서울 용산구 이태원로",
        "서울 종로구 세종대로",
        "서울 송파구 올림픽로",
    ]

    locations = []
    for i in range(10):
        lat, lon = random_coordinate()
        start_dt = random_date(start_days_ago=10, end_days_ahead=30)
        end_dt = start_dt + timedelta(days=random.randint(1, 7))

        location = Location(
            location_name=location_names[i],
            location_type=location_types[i % len(location_types)],
            address=addresses[i],
            latitude=lat,
            longitude=lon,
            start_datetime=start_dt,
            end_datetime=end_dt,
            description_summary=f"{location_names[i]}에서 진행되는 행사 및 영업 가능 장소입니다.",
        )
        db.session.add(location)
        locations.append(location)
        click.echo(f"  - Created: {location.location_name}")

    db.session.commit()

    # 4. Create 10 Documents
    click.echo("\nCreating 10 Documents...")
    doc_types = list(DocumentType)
    doc_statuses = list(DocumentStatus)
    sources = ["서울시청", "강남구청", "마포구청", "중구청", "종로구청"]

    documents = []
    for i in range(10):
        doc = Document(
            title=f"공문서 {i+1}호: {random.choice(['축제 공고', '영업 허가', '행사 안내', '규정 변경'])}",
            source=random.choice(sources),
            original_file_path=f"/documents/doc_{i+1}.pdf",
            ai_summary=f"이 문서는 {i+1}번째 공문서로, 푸드트럭 영업과 관련된 내용을 담고 있습니다.",
            document_type=doc_types[i % len(doc_types)],
            status=random.choice(doc_statuses),
            verified_by_admin_id=admin.admin_id if random.random() > 0.3 else None,
            published_at=datetime.now().date() - timedelta(days=random.randint(1, 60)),
            expires_at=datetime.now().date() + timedelta(days=random.randint(30, 365)),
            verified_at=(
                random_date(start_days_ago=5, end_days_ahead=0)
                if random.random() > 0.3
                else None
            ),
        )
        db.session.add(doc)
        documents.append(doc)
        click.echo(f"  - Created: {doc.title}")

    db.session.commit()

    # 5. Create DocumentLocation relations (10 entries)
    click.echo("\nCreating 10 Document-Location relations...")
    for i in range(10):
        doc = random.choice(documents)
        loc = random.choice(locations)

        # Check if relation already exists
        existing = DocumentLocation.query.filter_by(
            doc_id=doc.doc_id, location_id=loc.location_id
        ).first()

        if not existing:
            doc_loc = DocumentLocation(doc_id=doc.doc_id, location_id=loc.location_id)
            db.session.add(doc_loc)
            click.echo(f"  - Linked: {doc.title[:30]}... <-> {loc.location_name}")

    db.session.commit()

    # 6. Create FoodTruckLocation relations (10 entries)
    click.echo("\nCreating 10 FoodTruck-Location applications...")
    app_statuses = list(ApplicationStatus)

    for i in range(10):
        truck = random.choice(food_trucks)
        loc = random.choice(locations)

        # Check if relation already exists
        existing = FoodTruckLocation.query.filter_by(
            truck_id=truck.truck_id, location_id=loc.location_id
        ).first()

        if not existing:
            truck_loc = FoodTruckLocation(
                truck_id=truck.truck_id,
                location_id=loc.location_id,
                status=random.choice(app_statuses),
            )
            db.session.add(truck_loc)
            click.echo(
                f"  - Application: {truck.truck_name} -> {loc.location_name} "
                f"({truck_loc.status.value})"
            )

    db.session.commit()

    click.echo("\n✅ Dummy data seeded successfully!")
    click.echo(
        """
Summary:
  - Users: 1 (testuser)
  - Admins: 1 (admin@example.com)
  - Food Trucks: 10
  - Locations: 10
  - Documents: 10
  - Document-Location relations: 10
  - FoodTruck-Location applications: 10
"""
    )
