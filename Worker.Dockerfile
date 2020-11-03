FROM python:3.7-slim 

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app

CMD celery worker -A app.worker.celery_worker -l info -Q general
