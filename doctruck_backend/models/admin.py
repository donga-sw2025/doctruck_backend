from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from doctruck_backend.extensions import db, pwd_context


class Admin(db.Model):
    """Admin model - 관리자 정보 (사용자와 별도 테이블)"""

    __tablename__ = "admins"

    # Primary Key
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 관리자 계정 정보
    email = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 관리자 이름
    active = db.Column(db.Boolean, default=True)  # 계정 활성화 여부
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - 검증한 문서들
    verified_documents = db.relationship(
        "Document",
        foreign_keys="Document.verified_by_admin_id",
        back_populates="verified_by_admin",
        lazy="dynamic",
    )

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """비밀번호 자동 해싱 (User 모델과 동일한 방식)"""
        self._password = pwd_context.hash(value)

    def check_password(self, value):
        """비밀번호 검증"""
        return pwd_context.verify(value, self._password)

    def __repr__(self):
        return f"<Admin {self.name} ({self.email})>"
