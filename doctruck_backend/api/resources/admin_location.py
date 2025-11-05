"""Admin Location Resource - 관리자 전용 위치 관리 API

Spring Boot와 비교:
- Resource = @RestController
- admin_required = @PreAuthorize("hasRole('ADMIN')")

Spring 예시:
@RestController
@RequestMapping("/api/v1/admin/locations")
@PreAuthorize("hasRole('ADMIN')")
public class AdminLocationController {
    @PostMapping
    public LocationDto create(@RequestBody LocationDto dto) { }

    @PutMapping("/{id}")
    public LocationDto update(@PathVariable Long id, @RequestBody LocationDto dto) { }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) { }
}
"""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from doctruck_backend.api.schemas import LocationSchema
from doctruck_backend.models import Location
from doctruck_backend.extensions import db
from doctruck_backend.commons.pagination import paginate
from doctruck_backend.api.admin_helpers import admin_required


class AdminLocationList(Resource):
    """관리자 위치 목록 조회 및 등록

    ---
    get:
      tags:
        - admin-locations
      summary: 전체 위치 목록 조회 (관리자 전용)
      description: 모든 위치 목록을 조회합니다
      responses:
        200:
          description: 전체 위치 목록
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
        403:
          description: Admin permission required
    post:
      tags:
        - admin-locations
      summary: 새 위치 등록 (관리자 전용)
      description: 새로운 사업 위치를 등록합니다
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                location_name:
                  type: string
                  required: true
                  example: "여의도 한강공원"
                location_type:
                  type: string
                  enum: [FESTIVAL, PARK, MARKET, STREET, OTHER]
                  required: true
                address:
                  type: string
                  example: "서울시 영등포구 여의동로 330"
                latitude:
                  type: number
                  format: float
                  example: 37.5285
                longitude:
                  type: number
                  format: float
                  example: 126.9335
                operating_start_date:
                  type: string
                  format: date
                  example: "2024-05-01"
                operating_end_date:
                  type: string
                  format: date
                  example: "2024-10-31"
                max_capacity:
                  type: integer
                  example: 20
                application_deadline:
                  type: string
                  format: date
                description:
                  type: string
                contact_info:
                  type: string
      responses:
        201:
          description: 위치 생성 완료
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  location:
                    $ref: '#/components/schemas/LocationSchema'
        400:
          description: Bad request
        403:
          description: Admin permission required
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self):
        """전체 위치 목록 조회 (관리자용)"""
        schema = LocationSchema(many=True)
        query = Location.query.order_by(Location.created_at.desc())
        return paginate(query, schema)

    def post(self):
        """새 위치 등록 (관리자용)"""
        schema = LocationSchema()
        location = schema.load(request.json)

        db.session.add(location)
        db.session.commit()

        return {
            "message": "위치가 등록되었습니다.",
            "location": schema.dump(location)
        }, 201


class AdminLocationResource(Resource):
    """관리자 위치 상세 조회/수정/삭제

    ---
    get:
      tags:
        - admin-locations
      summary: 위치 상세 조회 (관리자 전용)
      description: 위치 상세 정보를 조회합니다
      parameters:
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
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
        403:
          description: Admin permission required
        404:
          description: Location not found
    put:
      tags:
        - admin-locations
      summary: 위치 수정 (관리자 전용)
      description: 위치 정보를 수정합니다
      parameters:
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                location_name:
                  type: string
                location_type:
                  type: string
                  enum: [FESTIVAL, PARK, MARKET, STREET, OTHER]
                address:
                  type: string
                latitude:
                  type: number
                  format: float
                longitude:
                  type: number
                  format: float
                operating_start_date:
                  type: string
                  format: date
                operating_end_date:
                  type: string
                  format: date
                max_capacity:
                  type: integer
                application_deadline:
                  type: string
                  format: date
                description:
                  type: string
                contact_info:
                  type: string
      responses:
        200:
          description: 위치 수정 완료
        403:
          description: Admin permission required
        404:
          description: Location not found
    delete:
      tags:
        - admin-locations
      summary: 위치 삭제 (관리자 전용)
      description: 위치를 삭제합니다
      parameters:
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
      responses:
        200:
          description: 위치 삭제 완료
        403:
          description: Admin permission required
        404:
          description: Location not found
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self, location_id):
        """위치 상세 조회 (관리자용)"""
        schema = LocationSchema()
        location = Location.query.get_or_404(location_id)
        return {"location": schema.dump(location)}, 200

    def put(self, location_id):
        """위치 수정 (관리자용)"""
        schema = LocationSchema(partial=True)
        location = Location.query.get_or_404(location_id)
        location = schema.load(request.json, instance=location)
        db.session.commit()
        return {"message": "위치가 수정되었습니다.", "location": schema.dump(location)}, 200

    def delete(self, location_id):
        """위치 삭제 (관리자용)"""
        location = Location.query.get_or_404(location_id)
        db.session.delete(location)
        db.session.commit()
        return {"message": "위치가 삭제되었습니다."}, 200
