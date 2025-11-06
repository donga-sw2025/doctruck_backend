"""중앙 집중식 에러 핸들러

Flask의 errorhandler와 JWT 콜백을 한 곳에서 관리합니다.
Spring의 @ControllerAdvice와 유사한 패턴입니다.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    InvalidHeaderError,
    JWTDecodeError,
    CSRFError,
    RevokedTokenError,
)


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
            jsonify(
                {"error": "csrf_error", "msg": "CSRF token validation failed"}
            ),
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
                {"error": "invalid_token", "msg": "Invalid token", "details": error_string}
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
