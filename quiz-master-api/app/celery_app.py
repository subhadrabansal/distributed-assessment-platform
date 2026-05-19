from app.extensions_celery import make_celery
from app import create_app

flask_app = create_app()
celery = make_celery(flask_app)

from app import celery_tasks
