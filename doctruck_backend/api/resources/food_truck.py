from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from doctruck_backend.api.schemas import FoodTruckSchema
from doctruck_backend.models import FoodTruck
from doctruck_backend.extensions import db
from doctruck_backend.commons.pagination import paginate


class FoodTruckResource(Resource):
    """단일 푸드트럭 리소스 - Spring의 @RestController와 유사

    Spring 비교:
    @RestController
    @RequestMapping("/api/v1/food-trucks")
    public class FoodTruckController {
        @GetMapping("/{id}")
        public FoodTruckDto getById(@PathVariable Long id) { }

        @PutMapping("/{id}")
        public FoodTruckDto update(@PathVariable Long id, @RequestBody FoodTruckDto dto) { }

        @DeleteMapping("/{id}")
        public void delete(@PathVariable Long id) { }
    }
    """

    method_decorators = [jwt_required()]  # Spring의 @PreAuthorize와 유사

    def get(self, truck_id):
        """푸드트럭 상세 조회

        Args:
            truck_id: 푸드트럭 ID (경로 파라미터)

        Returns:
            JSON: 푸드트럭 정보
        """
        schema = FoodTruckSchema()
        # 현재 로그인한 사용자
        current_user_id = get_jwt_identity()

        # 푸드트럭 조회
        food_truck = FoodTruck.query.get_or_404(truck_id)

        # 소유자 확인 (본인 것만 조회 가능)
        if food_truck.owner_id != current_user_id:
            return {"message": "권한이 없습니다."}, 403

        return {"food_truck": schema.dump(food_truck)}, 200

    def put(self, truck_id):
        """푸드트럭 수정

        Request Body:
            {
                "truck_name": "새로운 트럭 이름",
                "food_category": "한식",
                "operating_region": "서울"
            }
        """
        schema = FoodTruckSchema(partial=True)  # 부분 업데이트 허용
        current_user_id = get_jwt_identity()

        food_truck = FoodTruck.query.get_or_404(truck_id)

        # 권한 확인
        if food_truck.owner_id != current_user_id:
            return {"message": "권한이 없습니다."}, 403

        # JSON → 모델 업데이트
        food_truck = schema.load(request.json, instance=food_truck)
        db.session.commit()

        return {"message": "푸드트럭이 수정되었습니다.", "food_truck": schema.dump(food_truck)}, 200

    def delete(self, truck_id):
        """푸드트럭 삭제"""
        current_user_id = get_jwt_identity()

        food_truck = FoodTruck.query.get_or_404(truck_id)

        # 권한 확인
        if food_truck.owner_id != current_user_id:
            return {"message": "권한이 없습니다."}, 403

        db.session.delete(food_truck)
        db.session.commit()

        return {"message": "푸드트럭이 삭제되었습니다."}, 200


class FoodTruckList(Resource):
    """푸드트럭 목록 및 생성 - Spring의 @RestController와 유사

    Spring 비교:
    @GetMapping
    public List<FoodTruckDto> list() { }

    @PostMapping
    public FoodTruckDto create(@RequestBody FoodTruckDto dto) { }
    """

    method_decorators = [jwt_required()]

    def get(self):
        """내 푸드트럭 목록 조회

        Returns:
            JSON: 페이지네이션된 푸드트럭 목록
        """
        schema = FoodTruckSchema(many=True)
        current_user_id = get_jwt_identity()

        # 본인 소유 트럭만 조회
        query = FoodTruck.query.filter_by(owner_id=current_user_id)

        return paginate(query, schema)

    def post(self):
        """푸드트럭 등록

        Request Body:
            {
                "truck_name": "맛있는 푸드트럭",
                "business_registration_number": "123-45-67890",
                "food_category": "디저트",
                "operating_region": "서울"
            }
        """
        schema = FoodTruckSchema()
        current_user_id = get_jwt_identity()

        # JSON → 모델 변환
        food_truck = schema.load(request.json)

        # 소유자 설정 (현재 로그인한 사용자)
        food_truck.owner_id = current_user_id

        db.session.add(food_truck)
        db.session.commit()

        return {
            "message": "푸드트럭이 등록되었습니다.",
            "food_truck": schema.dump(food_truck)
        }, 201
