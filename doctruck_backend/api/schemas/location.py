"""Location Schema - Marshmallow 스키마

Spring Boot와 비교:
- Schema = DTO (Data Transfer Object)
- ma.SQLAlchemyAutoSchema = @ModelMapper (자동 변환)
- fields = DTO의 필드 선택
- dump_only = 응답 시에만 포함 (읽기 전용)

Spring 예시:
@Getter @Setter
public class LocationDto {
    private Long locationId;
    private String locationName;
    private LocationType locationType;
    // ...
}
"""

from doctruck_backend.models import Location
from doctruck_backend.extensions import ma, db


class LocationSchema(ma.SQLAlchemyAutoSchema):
    """Location 모델 직렬화/역직렬화 스키마"""

    class Meta:
        model = Location
        load_instance = True  # JSON → Location 객체 변환
        include_fk = True  # Foreign Key 포함
        sqla_session = db.session

        # 응답에 포함할 필드
        fields = (
            "location_id",
            "location_name",
            "location_type",
            "address",
            "latitude",
            "longitude",
            "operating_start_date",
            "operating_end_date",
            "max_capacity",
            "current_applicants",
            "application_deadline",
            "description",
            "contact_info",
            "created_at",
            "updated_at",
        )

        # 읽기 전용 필드 (생성/수정 시 무시됨)
        dump_only = (
            "location_id",
            "created_at",
            "updated_at",
            "current_applicants",  # 시스템이 자동 계산
        )

    # Enum을 문자열로 직렬화
    location_type = ma.Field()
