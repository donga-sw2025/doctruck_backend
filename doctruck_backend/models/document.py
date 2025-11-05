from datetime import datetime
import enum

from doctruck_backend.extensions import db


class DocumentType(enum.Enum):
    """문서 유형 - Spring의 enum과 동일"""

    POLICY = "POLICY"  # 정책
    NOTICE = "NOTICE"  # 공고
    REGULATION = "REGULATION"  # 규정
    EVENT = "EVENT"  # 행사
    OTHER = "OTHER"  # 기타


class DocumentStatus(enum.Enum):
    """문서 검증 상태 - Spring의 enum과 동일"""

    PENDING = "PENDING"  # 검증 대기 (AI가 수집한 상태)
    VERIFIED = "VERIFIED"  # 검증 완료 (관리자 승인)
    REJECTED = "REJECTED"  # 반려 (관리자가 거부)


class Document(db.Model):
    """Document model - 공문서 정보"""

    __tablename__ = "documents"

    # Primary Key
    doc_id = db.Column(db.BigInteger, primary_key=True)

    # 문서 기본 정보
    title = db.Column(db.String(255), nullable=False)  # 문서 제목
    source = db.Column(db.String(100), nullable=True)  # 출처 (예: '서울시청')
    original_file_path = db.Column(
        db.String(255), nullable=True
    )  # 원본 파일 경로 (OCR 대상)
    ai_summary = db.Column(db.Text, nullable=True)  # AI 요약본

    # 문서 분류 및 상태
    document_type = db.Column(
        db.Enum(DocumentType), nullable=False, default=DocumentType.OTHER
    )  # 문서 유형
    status = db.Column(
        db.Enum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING
    )  # 검증 상태

    # Foreign Key - 검증한 관리자
    verified_by_admin_id = db.Column(
        db.BigInteger,
        db.ForeignKey("admins.admin_id", ondelete="SET NULL"),
        nullable=True,
    )

    # 날짜 정보
    published_at = db.Column(db.Date, nullable=True)  # 공문서 게시일
    expires_at = db.Column(db.Date, nullable=True)  # 공문서 만료일
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )  # 시스템 등록일
    verified_at = db.Column(db.DateTime, nullable=True)  # 검증 일시

    # Relationships
    # Admin과의 관계 (N:1) - Spring의 @ManyToOne과 동일
    verified_by_admin = db.relationship(
        "Admin",
        foreign_keys=[verified_by_admin_id],
        back_populates="verified_documents",
    )

    # Location과의 관계 (N:M) - DocumentLocation을 통해 연결
    location_relations = db.relationship(
        "DocumentLocation",
        back_populates="document",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Document {self.title} ({self.status.value})>"
