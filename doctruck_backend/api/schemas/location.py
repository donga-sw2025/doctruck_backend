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

from marshmallow import fields as ma_fields
from doctruck_backend.models import Location
from doctruck_backend.extensions import ma, db


class LocationSchema(ma.SQLAlchemyAutoSchema):
    """Location 모델 직렬화/역직렬화 스키마"""

    # Enum을 문자열로 직렬화 (LocationType.FESTIVAL -> "FESTIVAL")
    # Meta 클래스보다 먼저 선언해야 제대로 오버라이드됨
    location_type = ma_fields.Method("get_location_type", deserialize="load_location_type")

    # Decimal을 Float로 직렬화 (db.Numeric -> float)
    latitude = ma_fields.Float()
    longitude = ma_fields.Float()

    class Meta:
        model = Location
        load_instance = True  # JSON → Location 객체 변환
        include_fk = True  # Foreign Key 포함
        sqla_session = db.session

        # 응답에 포함할 필드 (실제 모델의 필드와 일치)
        fields = (
            "location_id",
            "location_name",
            "location_type",
            "address",
            "latitude",
            "longitude",
            "start_datetime",
            "end_datetime",
            "description_summary",
            "created_at",
        )

        # 읽기 전용 필드 (생성/수정 시 무시됨)
        dump_only = (
            "location_id",
            "created_at",
        )

    def get_location_type(self, obj):
        """LocationType Enum을 문자열로 변환"""
        return obj.location_type.value if obj.location_type else None

    def load_location_type(self, value):
        """문자열을 LocationType Enum으로 변환"""
        from doctruck_backend.models.location import LocationType
        if value:
            try:
                return LocationType[value.upper()]
            except KeyError:
                return None
        return None
