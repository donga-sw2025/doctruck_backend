from flask import Flask
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

    configure_extensions(app)
    configure_cli(app)
    configure_apispec(app)
    register_blueprints(app)
    register_error_handlers(app, jwt)
    init_celery(app)

    return app


def configure_extensions(app):
    """Configure flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


def configure_cli(app):
    """Configure Flask 2.0's cli for easy entity management"""
    app.cli.add_command(manage.init)


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
