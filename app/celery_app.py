from app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("app","app.main.tasks")


app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'sync_all_users',
        'schedule': 15.0,
    },
}

app.conf.timezone ='UTC'

