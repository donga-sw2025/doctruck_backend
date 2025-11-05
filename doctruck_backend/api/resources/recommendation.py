"""Recommendation Resource - 맞춤 위치 추천 및 알림

Spring Boot와 비교:
- Resource = @RestController
- 추천 로직 = Service Layer (비즈니스 로직)

Spring 예시:
@RestController
@RequestMapping("/api/v1/recommendations")
public class RecommendationController {
    @GetMapping("/locations")
    public List<LocationDto> recommendLocations() {
        return recommendationService.getRecommendedLocations(userId);
    }
}
"""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from doctruck_backend.api.schemas import LocationSchema, DocumentSchema
from doctruck_backend.models import (
    FoodTruck,
    Location,
    Document,
    DocumentLocation,
    FoodTruckLocation,
)
from doctruck_backend.models.document import DocumentStatus
from datetime import datetime, timedelta


class RecommendedLocations(Resource):
    """맞춤 위치 추천 (핵심 기능)

    ---
    get:
      tags:
        - recommendations
      summary: 맞춤 위치 추천
      description: 사용자의 푸드트럭 정보를 기반으로 맞춤 위치를 추천합니다
      parameters:
        - in: query
          name: truck_id
          schema:
            type: integer
          required: false
          description: 특정 푸드트럭 기준 추천 (없으면 모든 트럭 고려)
        - in: query
          name: limit
          schema:
            type: integer
            default: 10
          description: 추천 개수 제한
      responses:
        200:
          description: 추천 위치 목록
          content:
            application/json:
              schema:
                type: object
                properties:
                  recommendations:
                    type: array
                    items:
                      type: object
                      properties:
                        location:
                          $ref: '#/components/schemas/LocationSchema'
                        score:
                          type: number
                          description: 추천 점수 (높을수록 좋음)
                        reason:
                          type: string
                          description: 추천 이유
        401:
          description: Unauthorized
    """

    method_decorators = [jwt_required()]

    def get(self):
        """맞춤 위치 추천 (사용자용)

        추천 알고리즘:
        1. 내 푸드트럭의 operating_region과 일치하는 위치 (높은 점수)
        2. 내 푸드트럭의 food_category와 관련된 위치 (중간 점수)
        3. 아직 신청 마감되지 않은 위치 (필수)
        4. 운영 기간이 곧 시작되는 위치 (우선순위)
        """
        current_user_id = get_jwt_identity()
        truck_id_filter = request.args.get("truck_id", type=int)
        limit = request.args.get("limit", default=10, type=int)

        # 내 푸드트럭 가져오기
        if truck_id_filter:
            trucks = FoodTruck.query.filter_by(
                truck_id=truck_id_filter, owner_id=current_user_id
            ).all()
            if not trucks:
                return {"message": "본인 소유의 푸드트럭이 아닙니다."}, 403
        else:
            trucks = FoodTruck.query.filter_by(owner_id=current_user_id).all()

        if not trucks:
            return {
                "message": "등록된 푸드트럭이 없습니다. 푸드트럭을 먼저 등록하세요.",
                "recommendations": [],
            }, 200

        # 이미 관심 등록한 위치 제외
        my_truck_ids = [t.truck_id for t in trucks]
        interested_location_ids = [
            rel.location_id
            for rel in FoodTruckLocation.query.filter(
                FoodTruckLocation.truck_id.in_(my_truck_ids)
            ).all()
        ]

        # 추천 가능한 위치 (신청 마감 안 된 위치)
        today = datetime.now().date()
        available_locations = Location.query.filter(
            or_(
                Location.application_deadline.is_(None),
                Location.application_deadline >= today,
            )
        ).all()

        # 점수 계산
        scored_locations = []
        for location in available_locations:
            # 이미 관심 등록한 위치는 제외
            if location.location_id in interested_location_ids:
                continue

            score = 0
            reasons = []

            for truck in trucks:
                # 1. 지역 매칭 (30점)
                if truck.operating_region and location.address:
                    if truck.operating_region.strip() in location.address:
                        score += 30
                        reasons.append(f"활동 지역({truck.operating_region}) 일치")

                # 2. 카테고리 매칭 (20점)
                # 예: 디저트 -> FESTIVAL, 한식 -> PARK
                if truck.food_category:
                    category_location_map = {
                        "디저트": "FESTIVAL",
                        "한식": "PARK",
                        "분식": "MARKET",
                    }
                    preferred_type = category_location_map.get(truck.food_category)
                    if (
                        preferred_type
                        and location.location_type.value == preferred_type
                    ):
                        score += 20
                        reasons.append(f"{truck.food_category} 카테고리에 적합한 위치")

            # 3. 운영 기간 임박 (10점)
            if location.operating_start_date:
                days_until_start = (location.operating_start_date - today).days
                if 0 <= days_until_start <= 30:
                    score += 10
                    reasons.append(f"{days_until_start}일 후 시작")

            # 4. 여유 공간 있음 (10점)
            if location.max_capacity and location.current_applicants:
                if location.current_applicants < location.max_capacity:
                    remaining = location.max_capacity - location.current_applicants
                    score += 10
                    reasons.append(f"잔여 {remaining}자리")

            # 5. 기본 점수 (모든 위치에 5점 - 최소 추천)
            score += 5
            if not reasons:
                reasons.append("새로운 사업 기회")

            scored_locations.append(
                {"location": location, "score": score, "reason": ", ".join(reasons)}
            )

        # 점수 순 정렬
        scored_locations.sort(key=lambda x: x["score"], reverse=True)

        # 상위 N개만
        top_recommendations = scored_locations[:limit]

        # Schema로 직렬화
        location_schema = LocationSchema()
        result = []
        for item in top_recommendations:
            result.append(
                {
                    "location": location_schema.dump(item["location"]),
                    "score": item["score"],
                    "reason": item["reason"],
                }
            )

        return {"recommendations": result, "count": len(result)}, 200


class RecommendedDocuments(Resource):
    """맞춤 공문서 알림 (핵심 기능)

    ---
    get:
      tags:
        - recommendations
      summary: 맞춤 공문서 알림
      description: 관심 위치 및 활동 지역을 기반으로 맞춤 공문서를 추천합니다
      parameters:
        - in: query
          name: days
          schema:
            type: integer
            default: 7
          description: 최근 N일 이내 VERIFIED된 문서만
      responses:
        200:
          description: 추천 공문서 목록
          content:
            application/json:
              schema:
                type: object
                properties:
                  recommendations:
                    type: array
                    items:
                      type: object
                      properties:
                        document:
                          $ref: '#/components/schemas/DocumentSchema'
                        reason:
                          type: string
                          description: 추천 이유
        401:
          description: Unauthorized
    """

    method_decorators = [jwt_required()]

    def get(self):
        """맞춤 공문서 알림 (사용자용)

        추천 알고리즘:
        1. 내 관심 위치와 연결된 문서
        2. 내 활동 지역과 관련된 문서
        3. 최근 VERIFIED된 문서 우선
        """
        current_user_id = get_jwt_identity()
        days = request.args.get("days", default=7, type=int)

        # 내 푸드트럭 가져오기
        my_trucks = FoodTruck.query.filter_by(owner_id=current_user_id).all()
        if not my_trucks:
            return {
                "message": "등록된 푸드트럭이 없습니다.",
                "recommendations": [],
            }, 200

        # 내 관심 위치 가져오기
        my_truck_ids = [t.truck_id for t in my_trucks]
        my_interested_locations = [
            rel.location_id
            for rel in FoodTruckLocation.query.filter(
                FoodTruckLocation.truck_id.in_(my_truck_ids)
            ).all()
        ]

        # 내 활동 지역
        my_regions = set()
        for truck in my_trucks:
            if truck.operating_region:
                my_regions.add(truck.operating_region.strip())

        # 최근 VERIFIED 문서
        since_date = datetime.now() - timedelta(days=days)
        recent_docs = Document.query.filter(
            Document.status == DocumentStatus.VERIFIED,
            Document.verified_at >= since_date,
        ).all()

        recommended_docs = []
        for doc in recent_docs:
            reasons = []

            # 1. 내 관심 위치와 연결된 문서인가?
            doc_locations = DocumentLocation.query.filter_by(doc_id=doc.doc_id).all()
            doc_location_ids = [rel.location_id for rel in doc_locations]

            for loc_id in my_interested_locations:
                if loc_id in doc_location_ids:
                    reasons.append("관심 등록한 위치와 관련됨")
                    break

            # 2. 내 활동 지역과 관련된 문서인가?
            if doc.source:
                for region in my_regions:
                    if region in doc.source:
                        reasons.append(f"활동 지역({region}) 관련 문서")
                        break

            # 추천 이유가 있는 것만
            if reasons:
                recommended_docs.append({"document": doc, "reason": ", ".join(reasons)})

        # Schema로 직렬화
        doc_schema = DocumentSchema()
        result = []
        for item in recommended_docs:
            result.append(
                {
                    "document": doc_schema.dump(item["document"]),
                    "reason": item["reason"],
                }
            )

        return {"recommendations": result, "count": len(result)}, 200
