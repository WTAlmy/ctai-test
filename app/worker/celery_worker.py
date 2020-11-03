import os

import uuid
import logging
from time import sleep

import boto3
import psycopg2
from celery import current_task

from .celery_app import celery_app


S3_BUCKET="will-public"
S3_ACCESS_KEY="AKIAJCYC6XTYNO6SJNPA"
S3_SECRET_ACCESS_KEY="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"

UPLOAD_FOLDER = "/app/uploads"

POSTGRES_HOST = os.environ.get("POSTGRES_SERVER")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_DBNAME = os.environ.get("POSTGRES_DB")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")


connection = psycopg2.connect(
  user = POSTGRES_USER,
  password = POSTGRES_PASSWORD,
  host = POSTGRES_HOST,
  port = "5432",
  database = POSTGRES_DBNAME,
)

logging.warning("Worker Database Running")

s3 = boto3.client(
  "s3",
  aws_access_key_id=S3_ACCESS_KEY,
  aws_secret_access_key=S3_SECRET_ACCESS_KEY
)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
  for i in range(1,15):
    sleep(1)
    current_task.update_state(state='PROGRESS',meta={'process_percent': i*10})
  return f"test task return {word}"


@celery_app.task(acks_late=True)
def upload_original_s3(file_path: str):
  logging.error("RECEIVED: " + file_path)
  with open(file_path, "rb") as f:
    unique_filename = uuid.uuid4().hex
    s3.upload_fileobj(f, S3_BUCKET, "test/"+unique_filename)
    cursor = connection.cursor()
    cursor.execute(f"""
      INSERT INTO uploads(original_s3)
      VALUES ('{unique_filename}')
      RETURNING id;
    """)
    connection.commit()
    cursor.close()
    logging.warning("CURSOR EXECUTED")
  if os.path.isfile(file_path):
    os.remove(file_path)
  else:
    logger.error("Previous File Not Found")









