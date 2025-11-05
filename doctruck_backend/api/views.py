from flask import Blueprint, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from doctruck_backend.extensions import apispec
from doctruck_backend.api.resources import (
    UserResource,
    UserList,
    FoodTruckResource,
    FoodTruckList,
    LocationResource,
    LocationList,
    DocumentResource,
    DocumentList,
    AdminDocumentPending,
    AdminDocumentVerify,
    AdminDocumentList,
    AdminDocumentResource,
    AdminLocationList,
    AdminLocationResource,
    AdminUserList,
    AdminUserResource,
    AdminDocumentLocationConnect,
    AdminDocumentLocationList,
    LocationInterest,
    MyLocationInterests,
    RecommendedLocations,
    RecommendedDocuments,
)
from doctruck_backend.api.schemas import (
    UserSchema,
    FoodTruckSchema,
    LocationSchema,
    DocumentSchema,
)


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


# User 라우트
api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")

# FoodTruck 라우트 (Spring의 @RequestMapping과 유사)
api.add_resource(FoodTruckList, "/food-trucks", endpoint="food_trucks")
api.add_resource(
    FoodTruckResource, "/food-trucks/<int:truck_id>", endpoint="food_truck_by_id"
)

# Location 라우트 (공개 API - 인증 불필요)
api.add_resource(LocationList, "/locations", endpoint="locations")
api.add_resource(
    LocationResource, "/locations/<int:location_id>", endpoint="location_by_id"
)

# Document 라우트 (공개 API - VERIFIED 문서만 조회 가능)
api.add_resource(DocumentList, "/documents", endpoint="documents")
api.add_resource(DocumentResource, "/documents/<int:doc_id>", endpoint="document_by_id")

# Admin Document 라우트 (관리자 전용)
api.add_resource(
    AdminDocumentPending, "/admin/documents/pending", endpoint="admin_documents_pending"
)
api.add_resource(
    AdminDocumentVerify,
    "/admin/documents/<int:doc_id>/verify",
    endpoint="admin_document_verify",
)
api.add_resource(AdminDocumentList, "/admin/documents", endpoint="admin_documents")
api.add_resource(
    AdminDocumentResource,
    "/admin/documents/<int:doc_id>",
    endpoint="admin_document_by_id",
)

# Admin Location 라우트 (관리자 전용)
api.add_resource(AdminLocationList, "/admin/locations", endpoint="admin_locations")
api.add_resource(
    AdminLocationResource,
    "/admin/locations/<int:location_id>",
    endpoint="admin_location_by_id",
)

# Admin User 라우트 (관리자 전용)
api.add_resource(AdminUserList, "/admin/users", endpoint="admin_users")
api.add_resource(
    AdminUserResource, "/admin/users/<int:user_id>", endpoint="admin_user_by_id"
)

# Admin Document-Location 연결 (관리자 전용)
api.add_resource(
    AdminDocumentLocationConnect,
    "/admin/documents/<int:doc_id>/locations/<int:location_id>",
    endpoint="admin_doc_location_connect",
)
api.add_resource(
    AdminDocumentLocationList,
    "/admin/documents/<int:doc_id>/locations",
    endpoint="admin_doc_locations",
)

# Location Interest (사용자 기능 - 위치 관심 등록)
api.add_resource(
    LocationInterest,
    "/locations/<int:location_id>/interest",
    endpoint="location_interest",
)
api.add_resource(MyLocationInterests, "/my/interests", endpoint="my_interests")

# Recommendations (사용자 기능 - 맞춤 추천)
api.add_resource(
    RecommendedLocations, "/recommendations/locations", endpoint="recommended_locations"
)
api.add_resource(
    RecommendedDocuments, "/recommendations/documents", endpoint="recommended_documents"
)


# Flask 3.0: before_app_first_request가 제거되어 record_once로 대체
@blueprint.record_once
def register_views(state):
    app = state.app
    # User 스키마 등록
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=app)
    apispec.spec.path(view=UserList, app=app)

    # FoodTruck 스키마 등록
    apispec.spec.components.schema("FoodTruckSchema", schema=FoodTruckSchema)
    apispec.spec.path(view=FoodTruckResource, app=app)
    apispec.spec.path(view=FoodTruckList, app=app)

    # Location 스키마 등록
    apispec.spec.components.schema("LocationSchema", schema=LocationSchema)
    apispec.spec.path(view=LocationResource, app=app)
    apispec.spec.path(view=LocationList, app=app)

    # Document 스키마 등록
    apispec.spec.components.schema("DocumentSchema", schema=DocumentSchema)
    apispec.spec.path(view=DocumentResource, app=app)
    apispec.spec.path(view=DocumentList, app=app)

    # Admin Document 경로 등록
    apispec.spec.path(view=AdminDocumentPending, app=app)
    apispec.spec.path(view=AdminDocumentVerify, app=app)
    apispec.spec.path(view=AdminDocumentList, app=app)
    apispec.spec.path(view=AdminDocumentResource, app=app)

    # Admin Location 경로 등록
    apispec.spec.path(view=AdminLocationList, app=app)
    apispec.spec.path(view=AdminLocationResource, app=app)

    # Admin User 경로 등록
    apispec.spec.path(view=AdminUserList, app=app)
    apispec.spec.path(view=AdminUserResource, app=app)

    # Admin Document-Location 경로 등록
    apispec.spec.path(view=AdminDocumentLocationConnect, app=app)
    apispec.spec.path(view=AdminDocumentLocationList, app=app)

    # Location Interest 경로 등록
    apispec.spec.path(view=LocationInterest, app=app)
    apispec.spec.path(view=MyLocationInterests, app=app)

    # Recommendations 경로 등록
    apispec.spec.path(view=RecommendedLocations, app=app)
    apispec.spec.path(view=RecommendedDocuments, app=app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
