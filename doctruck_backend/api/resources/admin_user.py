"""Admin User Resource - 관리자 전용 사용자 관리 API

Spring Boot와 비교:
- Resource = @RestController
- admin_required = @PreAuthorize("hasRole('ADMIN')")
"""

from flask_restful import Resource
from flask_jwt_extended import jwt_required

from doctruck_backend.api.schemas import UserSchema, FoodTruckSchema
from doctruck_backend.models import User, FoodTruck
from doctruck_backend.commons.pagination import paginate
from doctruck_backend.api.admin_helpers import admin_required


class AdminUserList(Resource):
    """관리자 사용자 목록 조회

    ---
    get:
      tags:
        - admin-users
      summary: 전체 사용자 목록 조회 (관리자 전용)
      description: 모든 사용자 목록을 조회합니다
      responses:
        200:
          description: 전체 사용자 목록
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
                          $ref: '#/components/schemas/UserSchema'
        403:
          description: Admin permission required
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self):
        """전체 사용자 목록 조회 (관리자용)"""
        schema = UserSchema(many=True)
        query = User.query.order_by(User.id.desc())
        return paginate(query, schema)


class AdminUserResource(Resource):
    """관리자 사용자 상세 조회

    ---
    get:
      tags:
        - admin-users
      summary: 사용자 상세 조회 (관리자 전용)
      description: 사용자 상세 정보와 소유 푸드트럭 목록을 조회합니다
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
          required: true
      responses:
        200:
          description: 사용자 상세 정보
          content:
            application/json:
              schema:
                type: object
                properties:
                  user:
                    $ref: '#/components/schemas/UserSchema'
                  food_trucks:
                    type: array
                    items:
                      $ref: '#/components/schemas/FoodTruckSchema'
        403:
          description: Admin permission required
        404:
          description: User not found
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self, user_id):
        """사용자 상세 조회 (관리자용 - 푸드트럭 목록 포함)"""
        user_schema = UserSchema()
        truck_schema = FoodTruckSchema(many=True)

        user = User.query.get_or_404(user_id)
        food_trucks = FoodTruck.query.filter_by(owner_id=user_id).all()

        return {
            "user": user_schema.dump(user),
            "food_trucks": truck_schema.dump(food_trucks),
        }, 200
