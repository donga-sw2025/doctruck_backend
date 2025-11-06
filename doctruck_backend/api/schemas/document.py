"""Document Schema - Marshmallow 스키마

Spring Boot와 비교:
- Schema = DTO (Data Transfer Object)
- ma.SQLAlchemyAutoSchema = @ModelMapper (자동 변환)
- fields = DTO의 필드 선택
- dump_only = 응답 시에만 포함 (읽기 전용)

Spring 예시:
@Getter @Setter
public class DocumentDto {
    private Long documentId;
    private String title;
    private DocumentType documentType;
    private DocumentStatus status;
    // ...
}
"""

from marshmallow import fields as ma_fields

from doctruck_backend.models import Document
from doctruck_backend.extensions import ma, db


class DocumentSchema(ma.SQLAlchemyAutoSchema):
    """Document 모델 직렬화/역직렬화 스키마"""

    # Enum을 문자열로 직렬화 (DocumentType.POLICY -> "POLICY")
    # Meta 클래스보다 먼저 선언해야 제대로 오버라이드됨
    document_type = ma_fields.Method(
        "get_document_type", deserialize="load_document_type"
    )
    status = ma_fields.Method("get_status", deserialize="load_status")

    class Meta:
        model = Document
        load_instance = True  # JSON → Document 객체 변환
        include_fk = True  # Foreign Key 포함
        sqla_session = db.session

        # 응답에 포함할 필드
        fields = (
            "doc_id",
            "title",
            "source",
            "original_file_path",
            "ai_summary",
            "document_type",
            "status",
            "verified_by_admin_id",
            "published_at",
            "expires_at",
            "created_at",
            "verified_at",
        )

        # 읽기 전용 필드 (생성/수정 시 무시됨)
        dump_only = (
            "doc_id",
            "status",  # 관리자만 변경 가능
            "verified_by_admin_id",  # 시스템이 자동 설정
            "verified_at",  # 시스템이 자동 설정
            "created_at",
        )

    def get_document_type(self, obj):
        """DocumentType Enum을 문자열로 변환"""
        return obj.document_type.value if obj.document_type else None

    def load_document_type(self, value):
        """문자열을 DocumentType Enum으로 변환"""
        from doctruck_backend.models.document import DocumentType

        if value:
            try:
                return DocumentType[value.upper()]
            except KeyError:
                return None
        return None

    def get_status(self, obj):
        """DocumentStatus Enum을 문자열로 변환"""
        return obj.status.value if obj.status else None

    def load_status(self, value):
        """문자열을 DocumentStatus Enum으로 변환"""
        from doctruck_backend.models.document import DocumentStatus

        if value:
            try:
                return DocumentStatus[value.upper()]
            except KeyError:
                return None
        return None
