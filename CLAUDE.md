# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based REST API backend called `doctruck_backend` that implements JWT authentication, user management, and background task processing with Celery. The project uses Flask-RESTful for API endpoints, SQLAlchemy for database operations, and includes OpenAPI/Swagger documentation.

## Development Commands

### Using Docker (Recommended)

```bash
# Build and start all services
make init

# Build Docker images
make build

# Start services (web, rabbitmq, redis, celery)
make run

# Run tests
make test

# Run linting
make lint

# Database migrations
make db-init      # Initialize migrations
make db-migrate   # Generate migration
make db-upgrade   # Apply migrations
```

### Direct Docker Compose

```bash
# Start services
docker-compose up -d

# Stop celery (needed before tests)
docker-compose stop celery

# Run commands in web container
docker-compose exec web flask db migrate
docker-compose exec web flask init  # Creates admin user

# Run tox tests
docker-compose run web tox -e test
```

### Testing

```bash
# Run all tests (automatically stops celery, starts rabbitmq/redis)
make test

# Run specific test file
docker-compose run -v $(PWD)/tests:/code/tests:ro web pytest tests/test_user.py

# Run with tox
make tox  # Uses py38 environment
```

## Architecture

### Application Factory Pattern

The app uses Flask's application factory pattern (`doctruck_backend/app.py:create_app()`). The factory:

1. Configures extensions (db, jwt, migrate)
2. Registers CLI commands
3. Sets up APISpec for Swagger
4. Registers blueprints (auth, api)
5. Initializes Celery with Flask context

### Extension Registry

All Flask extensions are initialized as singletons in `extensions.py` and configured in the application factory. This includes SQLAlchemy, JWT, Marshmallow, Migrate, Celery, and a custom APISpec extension.

### Blueprint Organization

- `auth` blueprint (`/auth`): Handles authentication (login, refresh, token revocation)
- `api` blueprint (`/api/v1`): REST resources for business logic (currently Users)

Each blueprint registers its views with APISpec for automatic OpenAPI documentation.

### Authentication Flow

JWT-based authentication with access/refresh token pattern:

1. User logs in via `/auth/login` → receives access + refresh tokens
2. Access tokens are used for API requests (short-lived)
3. Refresh tokens renew access tokens via `/auth/refresh`
4. Tokens are stored in database (models/blocklist.py) for revocation support
5. All API endpoints require JWT via `@jwt_required()` decorator

Token revocation is handled by the blocklist system - revoked tokens are checked via `@jwt.token_in_blocklist_loader` callback.

### Celery Integration

Celery is configured with Flask context awareness:

- `celery_app.py` initializes Celery and imports tasks
- `app.py:init_celery()` wraps tasks with Flask app context
- Tasks are defined in `tasks/` directory
- Uses RabbitMQ as broker and Redis as result backend (see docker-compose.yml)

When running tests, celery must be stopped to avoid conflicts with test tasks.

### Database Models

Models follow SQLAlchemy declarative pattern. Password hashing uses passlib's pbkdf2_sha256 scheme (configured in `extensions.py:pwd_context`).

### API Resources Pattern

Resources use Flask-RESTful's Resource class:

- Single resource classes (e.g., `UserResource`) handle GET/PUT/DELETE on `/resource/<id>`
- List resources (e.g., `UserList`) handle GET (paginated) and POST on `/resource`
- Marshmallow schemas handle serialization/deserialization
- Pagination helper in `commons/pagination.py` provides consistent paginated responses

### Custom APISpec Extension

`commons/apispec.py` provides:

- Custom `FlaskRestfulPlugin` to work with flask-restful resources
- Automatic OpenAPI spec generation from docstrings
- Swagger UI at `/swagger-ui`
- ReDoc UI at `/redoc-ui`
- OpenAPI spec at `/swagger.json` and `/openapi.yaml`

Docstrings in view functions use OpenAPI YAML syntax for documentation.

## Configuration

Configuration is environment-based via `config.py`:

- Uses environment variables (loaded via python-dotenv)
- `.flaskenv` for development settings
- `.testenv` for test settings
- Docker overrides via docker-compose.yml environment section

Key environment variables:
- `FLASK_ENV`: development/production
- `FLASK_APP`: doctruck_backend.app:create_app
- `DATABASE_URI`: SQLAlchemy database URL
- `SECRET_KEY`: Flask secret key for sessions/JWT
- `CELERY_BROKER_URL`: RabbitMQ connection URL
- `CELERY_RESULT_BACKEND_URL`: Redis connection URL

## Testing Strategy

Tests use pytest with pytest-flask, pytest-factoryboy, and pytest-celery:

- `conftest.py` sets up test fixtures and app configuration
- `factories.py` defines factory_boy factories for test data
- Tests run against in-memory SQLite (configured in tox.ini)
- Celery tests require RabbitMQ/Redis to be running

## Code Quality

Linting enforced via tox:
- flake8 with max line length 120
- black code formatter in check mode

Run `make lint` or `docker-compose run web tox -e lint` before committing.

## Initial Setup

After cloning, run `make init` which:
1. Builds Docker images
2. Starts all services (web, rabbitmq, redis, celery)
3. Initializes database migrations
4. Creates admin user (username: admin, email: pupajusang01@gmail.com)

The API will be available at http://localhost:5000.
