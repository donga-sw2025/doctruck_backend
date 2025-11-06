"""중앙 집중식 에러 핸들러

Flask의 errorhandler와 JWT 콜백을 한 곳에서 관리합니다.
Spring의 @ControllerAdvice와 유사한 패턴입니다.
"""

import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    InvalidHeaderError,
    JWTDecodeError,
    CSRFError,
    RevokedTokenError,
)

logger = logging.getLogger(__name__)


def register_error_handlers(app, jwt):
    """애플리케이션에 모든 에러 핸들러를 등록합니다

    Args:
        app: Flask application instance
        jwt: JWTManager instance
    """

    # ===== HTTP 예외 핸들러 =====

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """모든 HTTP 예외에 대한 기본 핸들러"""
        response = {"error": e.name, "msg": e.description, "status_code": e.code}
        return jsonify(response), e.code

    @app.errorhandler(400)
    def handle_bad_request(e):
        """400 Bad Request - JSON 파싱 오류 등"""
        # JSON 파싱 오류 감지
        error_msg = str(e.description) if e.description else "Bad request"

        # 더 명확한 에러 메시지
        if "JSON" in error_msg or "decode" in error_msg.lower():
            return (
                jsonify({
                    "error": "Invalid JSON",
                    "msg": "잘못된 JSON 형식입니다. 역슬래시(\\)를 제거하고 단일 따옴표를 사용하세요.",
                    "details": error_msg,
                    "example": "curl -d '{\"username\":\"testuser\",\"password\":\"testpass123\"}'"
                }),
                400,
            )

        return (
            jsonify({"error": "Bad Request", "msg": error_msg}),
            400,
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        """404 Not Found"""
        return (
            jsonify(
                {"error": "Not Found", "msg": "The requested resource was not found"}
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_internal_error(e):
        """500 Internal Server Error"""
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "msg": "An unexpected error occurred",
                }
            ),
            500,
        )

    # ===== JWT 관련 예외 핸들러 =====

    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        """Authorization 헤더가 없거나 잘못된 경우"""
        return (
            jsonify(
                {
                    "error": "unauthorized",
                    "msg": "Missing or invalid authorization header",
                }
            ),
            401,
        )

    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header_error(e):
        """JWT 헤더 형식이 잘못된 경우"""
        return (
            jsonify({"error": "invalid_header", "msg": "Invalid JWT header format"}),
            422,
        )

    @app.errorhandler(JWTDecodeError)
    def handle_jwt_decode_error(e):
        """JWT 디코딩 실패"""
        return (
            jsonify({"error": "invalid_token", "msg": "Token decoding failed"}),
            422,
        )

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """CSRF 토큰 오류"""
        return (
            jsonify({"error": "csrf_error", "msg": "CSRF token validation failed"}),
            401,
        )

    @app.errorhandler(RevokedTokenError)
    def handle_revoked_token_error(e):
        """무효화된 토큰 사용 시도"""
        return (
            jsonify({"error": "revoked_token", "msg": "Token has been revoked"}),
            401,
        )

    # ===== JWT 콜백 핸들러 =====

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        """인증되지 않은 요청 (Authorization 헤더 누락 등)"""
        return (
            jsonify(
                {
                    "error": "unauthorized",
                    "msg": "Missing or invalid authorization header",
                    "details": error_string,
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        """유효하지 않은 토큰"""
        return (
            jsonify(
                {
                    "error": "invalid_token",
                    "msg": "Invalid token",
                    "details": error_string,
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_headers, jwt_payload):
        """만료된 토큰"""
        return (
            jsonify(
                {
                    "error": "token_expired",
                    "msg": "Token has expired",
                    "token_type": jwt_payload.get("type", "access"),
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_headers, jwt_payload):
        """무효화된 토큰 (로그아웃된 토큰)"""
        return (
            jsonify({"error": "token_revoked", "msg": "Token has been revoked"}),
            401,
        )

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_headers, jwt_payload):
        """Fresh 토큰이 필요한 경우"""
        return (
            jsonify(
                {
                    "error": "fresh_token_required",
                    "msg": "Fresh token required for this operation",
                }
            ),
            401,
        )

    # ===== 일반 예외 핸들러 =====

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        """값 오류"""
        return jsonify({"error": "value_error", "msg": str(e)}), 400

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """모든 예외에 대한 최종 폴백 핸들러"""
        # 로그에 항상 상세한 에러 정보 기록 (프로덕션 디버깅용)
        logger.error(
            f"Unhandled exception: {type(e).__name__}: {str(e)}",
            exc_info=True,
            extra={"error_type": type(e).__name__},
        )

        # 개발 환경에서는 상세한 에러 메시지를, 프로덕션에서는 일반적인 메시지를
        if app.debug:
            return (
                jsonify(
                    {"error": "internal_error", "msg": str(e), "type": type(e).__name__}
                ),
                500,
            )
        else:
            return (
                jsonify(
                    {"error": "internal_error", "msg": "An unexpected error occurred"}
                ),
                500,
            )
