from celery import Celery


def make_celery(app_name=__name__):
    redis_uri = "redis://localhost:6379"
    return Celery(app_name, backend=redis_uri, broker=redis_uri)

def init_celery(celery, app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.context():
                return TaskBase.__call_(self, *args, **kwargs)
    celery.Task = ContextTask


