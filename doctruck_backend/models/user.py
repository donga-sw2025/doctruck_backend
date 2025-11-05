from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from doctruck_backend.extensions import db, pwd_context


class User(db.Model):
    """User model - 사용자(사업자) 정보"""

    __tablename__ = "user"  # 기존 테이블명 유지 (하위 호환성)

    # Primary Key - 기존 'id' 유지 (하위 호환성 위해)
    id = db.Column(db.Integer, primary_key=True)

    # 기존 컬럼 유지 (하위 호환성)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)

    # 새로운 컬럼 추가 (FUNCTIONAL_SPECS 기준)
    name = db.Column(db.String(100), nullable=True)  # 사업자명 또는 이름
    phone_number = db.Column(db.String(20), nullable=True)  # 연락처
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)  # 계정 생성일

    # Relationships - 푸드트럭과의 관계 (1:N)
    food_trucks = db.relationship("FoodTruck", back_populates="owner", lazy="dynamic")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
