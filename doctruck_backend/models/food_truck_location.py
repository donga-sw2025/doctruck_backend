from datetime import datetime
import enum

from doctruck_backend.extensions import db


class ApplicationStatus(enum.Enum):
    """신청/관심 상태 - Spring의 enum과 동일"""
    INTERESTED = "INTERESTED"  # 관심 있음
    APPLIED = "APPLIED"  # 신청 완료
    APPROVED = "APPROVED"  # 승인됨
    REJECTED = "REJECTED"  # 거절됨
    CANCELLED = "CANCELLED"  # 취소됨


class FoodTruckLocation(db.Model):
    """FoodTruckLocation model - 푸드트럭↔위치 관계 테이블 (N:M 관계 + 상태)

    Spring에서 추가 필드가 있는 @ManyToMany 중간 Entity와 동일
    사용자가 특정 위치에 관심 등록 또는 신청할 때 사용
    """

    __tablename__ = "food_truck_locations"

    # Primary Key
    application_id = db.Column(db.BigInteger, primary_key=True)

    # Foreign Keys
    truck_id = db.Column(
        db.BigInteger,
        db.ForeignKey("food_trucks.truck_id", ondelete="CASCADE"),
        nullable=False
    )
    location_id = db.Column(
        db.BigInteger,
        db.ForeignKey("locations.location_id", ondelete="CASCADE"),
        nullable=False
    )

    # 상태 정보 - 단순 관계가 아니라 비즈니스 로직이 포함된 관계
    status = db.Column(
        db.Enum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.INTERESTED
    )

    # 날짜 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 관심/신청 일시
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )  # 상태 변경 일시

    # Relationships
    food_truck = db.relationship("FoodTruck", back_populates="location_applications")
    location = db.relationship("Location", back_populates="truck_applications")

    # Unique constraint - 동일한 트럭-위치 조합 중복 방지
    __table_args__ = (
        db.UniqueConstraint("truck_id", "location_id", name="uq_truck_location"),
    )

    def __repr__(self):
        return f"<FoodTruckLocation truck_id={self.truck_id} location_id={self.location_id} status={self.status.value}>"
