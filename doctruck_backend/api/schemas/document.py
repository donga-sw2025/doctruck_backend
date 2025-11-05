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

from doctruck_backend.models import Document
from doctruck_backend.extensions import ma, db


class DocumentSchema(ma.SQLAlchemyAutoSchema):
    """Document 모델 직렬화/역직렬화 스키마"""

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

    # Enum을 문자열로 직렬화
    document_type = ma.Field()
    status = ma.Field()
