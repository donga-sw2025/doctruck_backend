from doctruck_backend.models import FoodTruck
from doctruck_backend.extensions import ma


class FoodTruckSchema(ma.SQLAlchemyAutoSchema):
    """FoodTruck Schema - Spring의 DTO와 동일한 역할

    Spring 비교:
    - Spring: @Data class FoodTruckDto { ... }
    - Flask: Marshmallow Schema

    자동으로 직렬화/역직렬화 처리:
    - JSON → Python 객체 (deserialization)
    - Python 객체 → JSON (serialization)
    """

    class Meta:
        model = FoodTruck
        # Spring의 @JsonIgnore와 유사
        load_instance = True  # JSON을 FoodTruck 모델 인스턴스로 변환
        include_fk = True  # Foreign Key 포함

        # 응답에 포함할 필드 지정
        fields = (
            "truck_id",
            "owner_id",
            "truck_name",
            "business_registration_number",
            "food_category",
            "operating_region",
            "created_at",
        )

        # 읽기 전용 필드 (Spring의 @JsonProperty(access = READ_ONLY))
        dump_only = ("truck_id", "created_at")
