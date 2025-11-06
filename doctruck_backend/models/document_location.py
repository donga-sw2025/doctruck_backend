from datetime import datetime

from doctruck_backend.extensions import db


class DocumentLocation(db.Model):
    """DocumentLocation model - 문서↔위치 관계 테이블 (N:M 관계)

    Spring에서의 @ManyToMany 중간 테이블과 동일한 역할
    관리자가 공문서를 특정 위치와 연결할 때 사용
    """

    __tablename__ = "document_locations"

    # Primary Key
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    doc_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.doc_id", ondelete="CASCADE"),
        nullable=False,
    )
    location_id = db.Column(
        db.Integer,
        db.ForeignKey("locations.location_id", ondelete="CASCADE"),
        nullable=False,
    )

    # 관계 생성 일시
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = db.relationship("Document", back_populates="location_relations")
    location = db.relationship("Location", back_populates="document_relations")

    # Unique constraint - 동일한 문서-위치 조합 중복 방지
    # Spring에서는 @Table(uniqueConstraints = {...})와 동일
    __table_args__ = (
        db.UniqueConstraint("doc_id", "location_id", name="uq_document_location"),
    )

    def __repr__(self):
        return f"<DocumentLocation doc_id={self.doc_id} location_id={self.location_id}>"
