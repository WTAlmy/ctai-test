import os

from celery import Celery

celery_app = Celery(
  "worker",
  backend="redis://:redis@redis:6379/0",
  broker="amqp://user:bitnami@rabbitmq:5672//"
)

celery_app.conf.task_routes = {
    "app.worker.celery_worker.test_celery": "general",
    "app.worker.celery_worker.upload_original_s3": "general"
}

celery_app.conf.update(task_track_started=True)
