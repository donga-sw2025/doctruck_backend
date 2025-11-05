from doctruck_backend.app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("doctruck_backend.tasks.example",)
