from celery import Celery, Task
from flask import Flask

# Integeration of celery with flask so all tasks can access the flask application
def celery_init_app(app: Flask) -> Celery:

    # The Task subclass automatically runs task functions with a Flask app context active, so that services like your database connections are available.
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config, namespace="CELERY")
    
    # Auto-discover tasks in app.celery_app.tasks module/file
    celery_app.autodiscover_tasks(['app.celery_app'], force=True)
    
    # Configure Celery Beat schedules (periodic tasks)
    # Note: send_email is NOT a periodic task - it's called on-demand when users register
    from celery.schedules import crontab
    
    celery_app.conf.beat_schedule = {
        # Daily report - runs every day at 9:00 AM
        'send-daily-report': {
            'task': 'app.celery_app.tasks.send_daily_report',
            'schedule': crontab(hour=9, minute=0),  # 9:00 AM every day
        },
        
        # Weekly report - runs every Monday at 9:00 AM
        'send-weekly-report': {
            'task': 'app.celery_app.tasks.send_weekly_report',
            'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday at 9:00 AM
        },
        
        # Cleanup expired jobs - runs every day at midnight
        'cleanup-expired-jobs': {
            'task': 'app.celery_app.tasks.cleanup_expired_jobs',
            'schedule': crontab(hour=0, minute=0),  # Midnight every day
        },

        'send' : {
            'task' : 'app.celery_app.tasks.send',
            'schedule' : 10.0
        }
        
    }
    
    # Where Beat stores its schedule file
    celery_app.conf.beat_schedule_filename = 'tmp/celerybeat-schedule'
    
    # Register tasks manually
    from app.celery_app import tasks
    celery_app.task(tasks.send_email, name='app.celery_app.tasks.send_email')
    celery_app.task(tasks.send_daily_report, name='app.celery_app.tasks.send_daily_report')
    celery_app.task(tasks.send_weekly_report, name='app.celery_app.tasks.send_weekly_report')
    celery_app.task(tasks.cleanup_expired_jobs, name='app.celery_app.tasks.cleanup_expired_jobs')
    #celery_app.task(tasks.send, name='app.celery_app.tasks.send')
    
    app.extensions["celery"] = celery_app
    return celery_app

 