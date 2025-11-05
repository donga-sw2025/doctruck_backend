from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from doctruck_backend.api.schemas import UserSchema
from doctruck_backend.models import User
from doctruck_backend.extensions import db
from doctruck_backend.commons.pagination import paginate


class UserResource(Resource):
    """사용자 리소스

    ---
    get:
      tags:
        - api
      summary: 사용자 조회
      description: ID로 사용자 정보를 조회합니다
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  user: UserSchema
        404:
          description: 사용자를 찾을 수 없음
    put:
      tags:
        - api
      summary: 사용자 수정
      description: ID로 사용자 정보를 수정합니다
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user updated
                  user: UserSchema
        404:
          description: 사용자를 찾을 수 없음
    delete:
      tags:
        - api
      summary: 사용자 삭제
      description: ID로 사용자를 삭제합니다
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user deleted
        404:
          description: 사용자를 찾을 수 없음
    """

    method_decorators = [jwt_required()]

    def get(self, user_id):
        schema = UserSchema()
        user = User.query.get_or_404(user_id)
        return {"user": schema.dump(user)}

    def put(self, user_id):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        user = schema.load(request.json, instance=user)

        db.session.commit()

        return {"msg": "user updated", "user": schema.dump(user)}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"msg": "user deleted"}


class UserList(Resource):
    """사용자 목록 리소스

    ---
    get:
      tags:
        - api
      summary: 사용자 목록 조회
      description: 페이지네이션된 사용자 목록을 조회합니다
      responses:
        200:
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
    post:
      tags:
        - api
      summary: 사용자 생성
      description: 새로운 사용자를 생성합니다
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user created
                  user: UserSchema
    """

    method_decorators = [jwt_required()]

    def get(self):
        schema = UserSchema(many=True)
        query = User.query
        return paginate(query, schema)

    def post(self):
        schema = UserSchema()
        user = schema.load(request.json)

        db.session.add(user)
        db.session.commit()

        return {"msg": "user created", "user": schema.dump(user)}, 201
