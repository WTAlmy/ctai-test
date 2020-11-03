import os
import uuid
import logging
from typing import List, Optional

import psycopg2
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .worker.celery_app import celery_app

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

logging.warning("Database Running")
cursor = connection.cursor()

UPLOAD_FOLDER = "/app/uploads"
ALLOWED_EXTENSIONS = {"mp4", "mov", "mpeg", "webm", "avi", "wmv", "flv"}

app = FastAPI()
templates = Jinja2Templates(directory="/app/templates")


def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.on_event("shutdown")
def shutdown_event():
  if (connection):
    cursor.close()
    connection.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})

@app.get("/test")
def queue_test(word: str):
  task_name = "app.worker.celery_worker.test_celery"
  task = celery_app.send_task(task_name, args=[word])
  return {"message": "test completed"}

@app.get("/list")
def db_list():
  cursor.execute("""SELECT * FROM uploads""")
  return {"message": str(cursor.fetchall())}

@app.post("/msg/{message}")
def write_root(message: str):
  return {"message": message}

@app.post("/", response_class=RedirectResponse)
async def upload_files(files: List[UploadFile] = File(...)):
  for uploaded_file in files:
    if allowed_file(uploaded_file.filename):
      file_name = uuid.uuid4().hex
      file_path = os.path.join(UPLOAD_FOLDER, file_name)
      with open(file_path, 'wb') as f:
        f.write(await uploaded_file.read())
        task_name = "app.worker.celery_worker.upload_original_s3"
        logging.error("SENT PATH:" + file_path)
        celery_app.send_task(task_name, args=[file_path])
  return RedirectResponse(url="/msg/success")

