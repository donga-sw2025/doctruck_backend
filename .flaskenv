FLASK_ENV=development
FLASK_APP=doctruck_backend.app:create_app
SECRET_KEY=changeme
DATABASE_URI=sqlite:///doctruck_backend.db
CELERY_BROKER_URL=amqp://guest:guest@localhost/
CELERY_RESULT_BACKEND_URL=rpc://
