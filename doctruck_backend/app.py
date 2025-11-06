import logging
import time
from flask import Flask, request, g
from doctruck_backend import api
from doctruck_backend import auth
from doctruck_backend import manage
from doctruck_backend.extensions import apispec
from doctruck_backend.extensions import db
from doctruck_backend.extensions import jwt
from doctruck_backend.extensions import migrate, celery
from doctruck_backend.errors import register_error_handlers


def create_app(testing=False):
    """Application factory, used to create application"""
    app = Flask("doctruck_backend")
    app.config.from_object("doctruck_backend.config")

    if testing is True:
        app.config["TESTING"] = True

    configure_logging(app)
    configure_extensions(app)
    configure_cli(app)
    configure_apispec(app)
    register_blueprints(app)
    register_error_handlers(app, jwt)
    register_request_logging(app)
    init_celery(app)

    return app


def configure_logging(app):
    """Configure application logging"""
    # 기본 로깅 레벨 설정
    if app.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Flask 앱 로거 설정
    app.logger.setLevel(log_level)

    # 콘솔 핸들러 추가 (gunicorn에서 stdout으로 출력)
    if not app.logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)

    # 다른 모듈의 로거도 동일한 레벨로 설정
    logging.getLogger("doctruck_backend").setLevel(log_level)


def configure_extensions(app):
    """Configure flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


def configure_cli(app):
    """Configure Flask 2.0's cli for easy entity management"""
    from doctruck_backend.seed_data import seed_dummy_data

    app.cli.add_command(manage.init)
    app.cli.add_command(seed_dummy_data)


def configure_apispec(app):
    """Configure APISpec for swagger support"""
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def register_blueprints(app):
    """Register all blueprints for application"""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)
    register_health_check(app)


def register_request_logging(app):
    """Register request/response logging middleware"""
    logger = logging.getLogger(__name__)

    @app.before_request
    def log_request_info():
        """요청 시작 시 로깅"""
        # 요청 시작 시간 저장
        g.start_time = time.time()

        # 헬스체크는 로깅하지 않음 (노이즈 방지)
        if request.path == "/health":
            return

        # 요청 정보 로깅
        logger.info(
            f"REQUEST: {request.method} {request.path} "
            f"from {request.remote_addr} "
            f"User-Agent: {request.headers.get('User-Agent', 'N/A')}"
        )

        # 요청 바디 로깅 (민감한 정보는 마스킹)
        if request.is_json and request.method in ["POST", "PUT", "PATCH"]:
            try:
                data = request.get_json()
                # 비밀번호 필드 마스킹
                if isinstance(data, dict):
                    safe_data = data.copy()
                    for key in ["password", "old_password", "new_password"]:
                        if key in safe_data:
                            safe_data[key] = "***MASKED***"
                    logger.debug(f"REQUEST BODY: {safe_data}")
            except Exception:
                pass

    @app.after_request
    def log_response_info(response):
        """응답 전송 전 로깅"""
        # 헬스체크는 로깅하지 않음
        if request.path == "/health":
            return response

        # 요청 처리 시간 계산
        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time
            elapsed_ms = round(elapsed * 1000, 2)
        else:
            elapsed_ms = 0

        # 응답 정보 로깅
        logger.info(
            f"RESPONSE: {request.method} {request.path} "
            f"Status={response.status_code} "
            f"Time={elapsed_ms}ms"
        )

        return response


def register_health_check(app):
    """Register health check endpoint for Docker healthcheck"""

    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Docker 헬스 체크용 엔드포인트
        인증 없이 접근 가능하며, 컨테이너의 건강 상태를 확인합니다.

        ---
        get:
          tags:
            - health
          summary: 헬스 체크
          description: 컨테이너가 정상적으로 동작하는지 확인하는 엔드포인트
          responses:
            200:
              description: 서버가 정상 동작 중
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      status:
                        type: string
                        example: healthy
          security: []
        """
        return {"status": "healthy"}, 200


def init_celery(app=None):
    app = app or create_app()

    # Update Celery configuration from Flask config
    celery_config = app.config.get("CELERY", {})
    celery.conf.broker_url = celery_config.get("broker_url")
    celery.conf.result_backend = celery_config.get("result_backend")
    celery.conf.update(celery_config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
