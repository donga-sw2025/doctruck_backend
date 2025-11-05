from datetime import datetime

from doctruck_backend.extensions import db


class FoodTruck(db.Model):
    """FoodTruck model - 푸드트럭 정보"""

    __tablename__ = "food_trucks"

    # Primary Key
    truck_id = db.Column(db.BigInteger, primary_key=True)

    # Foreign Key - 소유자 (User)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    # 푸드트럭 기본 정보
    truck_name = db.Column(db.String(100), nullable=False)  # 푸드트럭 이름
    business_registration_number = db.Column(
        db.String(50), nullable=True
    )  # 사업자 등록 번호
    food_category = db.Column(
        db.String(50), nullable=True
    )  # 음식 카테고리 (예: '디저트', '한식')
    operating_region = db.Column(
        db.String(100), nullable=True
    )  # 주 활동 지역 (예: '서울', '경기')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    # User와의 관계 (N:1) - Spring의 @ManyToOne과 동일
    owner = db.relationship("User", back_populates="food_trucks")

    # Location과의 관계 (N:M) - FoodTruckLocation을 통해 연결
    location_applications = db.relationship(
        "FoodTruckLocation",
        back_populates="food_truck",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<FoodTruck {self.truck_name} (Category: {self.food_category})>"
