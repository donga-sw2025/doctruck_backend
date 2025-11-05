"""FoodTruck-Location Interest Resource - 위치 관심 등록 (사용자 기능)

Spring Boot와 비교:
- Resource = @RestController
- jwt_required = @PreAuthorize("isAuthenticated()")

Spring 예시:
@RestController
@RequestMapping("/api/v1/locations/{locationId}/interest")
public class LocationInterestController {
    @PostMapping
    public void registerInterest(@PathVariable Long locationId, @RequestParam Long truckId) { }

    @DeleteMapping
    public void cancelInterest(@PathVariable Long locationId, @RequestParam Long truckId) { }
}
"""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from doctruck_backend.models import FoodTruck, Location, FoodTruckLocation
from doctruck_backend.models.food_truck_location import ApplicationStatus
from doctruck_backend.extensions import db


class LocationInterest(Resource):
    """위치 관심 등록/취소 (사용자 기능)

    ---
    post:
      tags:
        - location-interest
      summary: 위치 관심 등록
      description: 특정 푸드트럭으로 위치에 관심 등록(INTERESTED 상태)을 합니다
      parameters:
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
          description: 위치 ID
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                truck_id:
                  type: integer
                  required: true
                  description: 푸드트럭 ID (본인 소유 트럭)
      responses:
        201:
          description: 관심 등록 완료
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  application_id:
                    type: integer
        400:
          description: Bad request (already registered, not owner, etc.)
        401:
          description: Unauthorized
        404:
          description: Location or Truck not found
    delete:
      tags:
        - location-interest
      summary: 위치 관심 취소
      description: 위치 관심 등록을 취소합니다
      parameters:
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
        - in: query
          name: truck_id
          schema:
            type: integer
          required: true
      responses:
        200:
          description: 관심 취소 완료
        401:
          description: Unauthorized
        404:
          description: Interest not found
    """

    method_decorators = [jwt_required()]

    def post(self, location_id):
        """위치 관심 등록 (사용자용)"""
        current_user_id = get_jwt_identity()
        truck_id = request.json.get("truck_id")

        if not truck_id:
            return {"message": "truck_id가 필요합니다."}, 400

        # 위치 존재 확인
        Location.query.get_or_404(location_id)

        # 트럭 존재 및 소유권 확인
        truck = FoodTruck.query.get_or_404(truck_id)
        if truck.owner_id != current_user_id:
            return {"message": "본인 소유의 푸드트럭만 사용할 수 있습니다."}, 403

        # 이미 등록되어 있는지 확인
        existing = FoodTruckLocation.query.filter_by(
            truck_id=truck_id, location_id=location_id
        ).first()

        if existing:
            return {"message": "이미 관심 등록된 위치입니다."}, 400

        # 새 관심 등록 (INTERESTED 상태)
        interest = FoodTruckLocation(
            truck_id=truck_id,
            location_id=location_id,
            status=ApplicationStatus.INTERESTED,
        )
        db.session.add(interest)
        db.session.commit()

        return {
            "message": "위치 관심 등록이 완료되었습니다.",
            "application_id": interest.application_id,
        }, 201

    def delete(self, location_id):
        """위치 관심 취소 (사용자용)"""
        current_user_id = get_jwt_identity()
        truck_id = request.args.get("truck_id", type=int)

        if not truck_id:
            return {"message": "truck_id가 필요합니다."}, 400

        # 트럭 소유권 확인
        truck = FoodTruck.query.get_or_404(truck_id)
        if truck.owner_id != current_user_id:
            return {"message": "본인 소유의 푸드트럭만 관리할 수 있습니다."}, 403

        # 관심 등록 찾기
        interest = FoodTruckLocation.query.filter_by(
            truck_id=truck_id, location_id=location_id
        ).first_or_404()

        db.session.delete(interest)
        db.session.commit()

        return {"message": "위치 관심 등록이 취소되었습니다."}, 200


class MyLocationInterests(Resource):
    """내 관심 위치 목록 조회

    ---
    get:
      tags:
        - location-interest
      summary: 내 관심 위치 목록 조회
      description: 내가 관심 등록한 위치 목록을 조회합니다
      parameters:
        - in: query
          name: truck_id
          schema:
            type: integer
          required: false
          description: 특정 푸드트럭의 관심 위치만 조회 (선택)
      responses:
        200:
          description: 내 관심 위치 목록
          content:
            application/json:
              schema:
                type: object
                properties:
                  interests:
                    type: array
                    items:
                      type: object
                      properties:
                        application_id:
                          type: integer
                        truck_id:
                          type: integer
                        location_id:
                          type: integer
                        status:
                          type: string
        401:
          description: Unauthorized
    """

    method_decorators = [jwt_required()]

    def get(self):
        """내 관심 위치 목록 조회 (사용자용)"""
        current_user_id = get_jwt_identity()

        # 내 트럭 목록
        my_trucks = FoodTruck.query.filter_by(owner_id=current_user_id).all()
        my_truck_ids = [t.truck_id for t in my_trucks]

        if not my_truck_ids:
            return {"interests": [], "count": 0}, 200

        # 특정 트럭 필터 (선택)
        truck_id_filter = request.args.get("truck_id", type=int)
        if truck_id_filter:
            if truck_id_filter not in my_truck_ids:
                return {"message": "본인 소유의 푸드트럭이 아닙니다."}, 403
            query = FoodTruckLocation.query.filter_by(truck_id=truck_id_filter)
        else:
            query = FoodTruckLocation.query.filter(
                FoodTruckLocation.truck_id.in_(my_truck_ids)
            )

        interests = query.all()

        result = []
        for interest in interests:
            result.append(
                {
                    "application_id": interest.application_id,
                    "truck_id": interest.truck_id,
                    "location_id": interest.location_id,
                    "status": interest.status.value,
                    "created_at": (
                        interest.created_at.isoformat() if interest.created_at else None
                    ),
                }
            )

        return {"interests": result, "count": len(result)}, 200
