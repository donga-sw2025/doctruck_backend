"""Location Resource - Flask-RESTful API 엔드포인트

Spring Boot와 비교:
- Resource = @RestController
- method_decorators = @PreAuthorize (권한 제어)
- get() = @GetMapping
- Resource 클래스 = Controller 클래스

Spring 예시:
@RestController
@RequestMapping("/api/v1/locations")
public class LocationController {
    @GetMapping
    public List<LocationDto> list() { }

    @GetMapping("/{id}")
    public LocationDto getById(@PathVariable Long id) { }
}
"""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_

from doctruck_backend.api.schemas import LocationSchema
from doctruck_backend.models import Location
from doctruck_backend.extensions import db
from doctruck_backend.commons.pagination import paginate
from datetime import datetime


class LocationResource(Resource):
    """단일 위치 리소스 - 상세 조회

    ---
    get:
      tags:
        - locations
      summary: 위치 상세 조회
      description: 특정 위치의 상세 정보를 조회합니다
      parameters:
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
          description: 위치 ID
      responses:
        200:
          description: 위치 상세 정보
          content:
            application/json:
              schema:
                type: object
                properties:
                  location:
                    $ref: '#/components/schemas/LocationSchema'
        404:
          description: 위치를 찾을 수 없음
    """

    # 인증 불필요 (사용자 기능: 누구나 위치 조회 가능)
    # Spring의 permitAll()과 유사

    def get(self, location_id):
        """위치 상세 조회 (Spring의 @GetMapping과 유사)"""
        schema = LocationSchema()
        location = Location.query.get_or_404(location_id)

        return {"location": schema.dump(location)}, 200


class LocationList(Resource):
    """위치 목록 조회 - 필터링 및 검색 지원

    ---
    get:
      tags:
        - locations
      summary: 위치 목록 조회
      description: 페이지네이션과 필터링을 지원하는 위치 목록을 조회합니다
      parameters:
        - in: query
          name: location_type
          schema:
            type: string
            enum: [FESTIVAL, PARK, MARKET, STREET, OTHER]
          required: false
          description: 위치 유형 필터
        - in: query
          name: start_date
          schema:
            type: string
            format: date
          required: false
          description: 운영 시작일 필터 (YYYY-MM-DD)
        - in: query
          name: end_date
          schema:
            type: string
            format: date
          required: false
          description: 운영 종료일 필터 (YYYY-MM-DD)
        - in: query
          name: search
          schema:
            type: string
          required: false
          description: 검색어 (위치명 또는 주소)
        - in: query
          name: page
          schema:
            type: integer
            default: 1
          description: 페이지 번호
        - in: query
          name: per_page
          schema:
            type: integer
            default: 10
          description: 페이지당 개수
      responses:
        200:
          description: 위치 목록
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/LocationSchema'
    """

    # 인증 불필요 (공개 API)

    def get(self):
        """위치 목록 조회 (필터링 지원 - Spring의 @GetMapping + @RequestParam과 유사)"""
        schema = LocationSchema(many=True)

        # 기본 쿼리
        query = Location.query

        # 1. 위치 유형 필터 (Spring의 @RequestParam)
        location_type = request.args.get("location_type")
        if location_type:
            # Enum 값으로 필터링
            from doctruck_backend.models.location import LocationType
            try:
                location_type_enum = LocationType[location_type.upper()]
                query = query.filter(Location.location_type == location_type_enum)
            except KeyError:
                return {"message": f"Invalid location_type: {location_type}"}, 400

        # 2. 날짜 범위 필터 (운영 기간 내 위치 검색)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                # 운영 종료일이 시작일 이후인 위치 (아직 종료 안 된 것)
                query = query.filter(
                    or_(
                        Location.operating_end_date >= start_date_obj,
                        Location.operating_end_date.is_(None)  # 종료일 없음 = 상시 운영
                    )
                )
            except ValueError:
                return {"message": "Invalid start_date format. Use YYYY-MM-DD"}, 400

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                # 운영 시작일이 종료일 이전인 위치 (아직 시작 전인 것도 포함)
                query = query.filter(
                    or_(
                        Location.operating_start_date <= end_date_obj,
                        Location.operating_start_date.is_(None)
                    )
                )
            except ValueError:
                return {"message": "Invalid end_date format. Use YYYY-MM-DD"}, 400

        # 3. 검색어 필터 (위치명 또는 주소에서 검색)
        search = request.args.get("search")
        if search:
            # Spring의 JPA Specification과 유사
            search_filter = or_(
                Location.location_name.ilike(f"%{search}%"),
                Location.address.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # 4. 최신순 정렬 (생성일 기준)
        query = query.order_by(Location.created_at.desc())

        # 5. 페이지네이션 (Spring의 Pageable과 유사)
        return paginate(query, schema)
