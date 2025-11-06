from datetime import datetime
import enum

from doctruck_backend.extensions import db


class LocationType(enum.Enum):
    """위치 유형 - Spring의 enum과 동일한 개념"""

    FESTIVAL = "FESTIVAL"  # 축제
    PARK = "PARK"  # 공원
    MARKET = "MARKET"  # 시장
    STREET = "STREET"  # 거리
    OTHER = "OTHER"  # 기타


class Location(db.Model):
    """Location model - 사업 가능 위치 정보"""

    __tablename__ = "locations"

    # Primary Key
    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 위치 기본 정보
    location_name = db.Column(
        db.String(255), nullable=False
    )  # 위치 이름 (예: '여의도 한강공원')
    location_type = db.Column(
        db.Enum(LocationType), nullable=False, default=LocationType.OTHER
    )  # 위치 유형
    address = db.Column(db.String(255), nullable=True)  # 주소

    # 좌표 정보 (추천 시스템 핵심) - PostGIS로 향후 마이그레이션 가능
    # DECIMAL(9,6) = 소수점 이하 6자리 (약 10cm 정밀도)
    latitude = db.Column(db.Numeric(9, 6), nullable=True)  # 위도
    longitude = db.Column(db.Numeric(9, 6), nullable=True)  # 경도

    # 행사 일정 정보
    start_datetime = db.Column(db.DateTime, nullable=True)  # 행사 시작 일시
    end_datetime = db.Column(db.DateTime, nullable=True)  # 행사 종료 일시

    # 요약 정보
    description_summary = db.Column(db.Text, nullable=True)  # 요약 정보

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    # Document와의 관계 (N:M) - DocumentLocation을 통해 연결
    document_relations = db.relationship(
        "DocumentLocation",
        back_populates="location",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # FoodTruck과의 관계 (N:M) - FoodTruckLocation을 통해 연결
    truck_applications = db.relationship(
        "FoodTruckLocation",
        back_populates="location",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Location {self.location_name} ({self.location_type.value})>"
