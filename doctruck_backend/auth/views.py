from flask import request, jsonify, Blueprint, current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from doctruck_backend.models import User, Admin
from doctruck_backend.extensions import pwd_context, jwt, apispec
from doctruck_backend.auth.helpers import (
    revoke_token,
    is_token_revoked,
    add_token_to_database,
)


blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/login", methods=["POST"])
def login():
    """사용자 로그인

    ---
    post:
      tags:
        - auth
      summary: 사용자 로그인
      description: 사용자 인증 정보로 로그인하여 액세스 토큰과 리프레시 토큰을 발급받습니다
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: myuser
                  required: true
                password:
                  type: string
                  example: P4$$w0rd!
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
                  refresh_token:
                    type: string
                    example: myrefreshtoken
        400:
          description: 잘못된 요청
      security: []
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not pwd_context.verify(password, user.password):
        return jsonify({"msg": "Bad credentials"}), 400

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    add_token_to_database(refresh_token, app.config["JWT_IDENTITY_CLAIM"])

    ret = {"access_token": access_token, "refresh_token": refresh_token}
    return jsonify(ret), 200


@blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """액세스 토큰 갱신

    ---
    post:
      tags:
        - auth
      summary: 액세스 토큰 갱신
      description: Authorization 헤더의 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
        400:
          description: 잘못된 요청
        401:
          description: 인증 실패
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    ret = {"access_token": access_token}
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    return jsonify(ret), 200


@blueprint.route("/revoke_access", methods=["DELETE"])
@jwt_required()
def revoke_access_token():
    """액세스 토큰 무효화

    ---
    delete:
      tags:
        - auth
      summary: 액세스 토큰 무효화
      description: 현재 액세스 토큰을 무효화합니다
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: token revoked
        400:
          description: 잘못된 요청
        401:
          description: 인증 실패
    """
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@blueprint.route("/revoke_refresh", methods=["DELETE"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    """리프레시 토큰 무효화 (로그아웃)

    ---
    delete:
      tags:
        - auth
      summary: 리프레시 토큰 무효화
      description: 리프레시 토큰을 무효화합니다 (주로 로그아웃 시 사용)
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: token revoked
        400:
          description: 잘못된 요청
        401:
          description: 인증 실패
    """
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@blueprint.route("/admin/login", methods=["POST"])
def admin_login():
    """관리자 로그인

    ---
    post:
      tags:
        - auth
      summary: 관리자 로그인
      description: 관리자 인증 정보로 로그인하여 관리자 권한 토큰을 발급받습니다
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  example: admin@example.com
                  required: true
                password:
                  type: string
                  example: adminpassword
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myadminaccesstoken
                  refresh_token:
                    type: string
                    example: myadminrefreshtoken
                  admin_id:
                    type: integer
                  name:
                    type: string
        400:
          description: 잘못된 요청
        401:
          description: 인증 실패
      security: []
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    admin = Admin.query.filter_by(email=email).first()
    if admin is None or not admin.check_password(password):
        return jsonify({"msg": "Bad admin credentials"}), 401

    if not admin.active:
        return jsonify({"msg": "Admin account is inactive"}), 401

    # admin_id를 identity로 사용하되, role을 구분하기 위해 "admin:" prefix 추가
    # Spring의 GrantedAuthority와 유사
    admin_identity = f"admin:{admin.admin_id}"
    access_token = create_access_token(identity=admin_identity)
    refresh_token = create_refresh_token(identity=admin_identity)
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    add_token_to_database(refresh_token, app.config["JWT_IDENTITY_CLAIM"])

    ret = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "admin_id": admin.admin_id,
        "name": admin.name,
    }
    return jsonify(ret), 200


@jwt.user_lookup_loader
def user_loader_callback(jwt_headers, jwt_payload):
    identity = jwt_payload["sub"]
    return User.query.get(identity)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_headers, jwt_payload):
    return is_token_revoked(jwt_payload)


# Flask 3.0: before_app_first_request가 제거되어 record_once로 대체
@blueprint.record_once
def register_views(state):
    app_instance = state.app
    apispec.spec.path(view=login, app=app_instance)
    apispec.spec.path(view=refresh, app=app_instance)
    apispec.spec.path(view=revoke_access_token, app=app_instance)
    apispec.spec.path(view=revoke_refresh_token, app=app_instance)
    apispec.spec.path(view=admin_login, app=app_instance)
