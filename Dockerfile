FROM python:3.7-slim 

COPY ./requirements.txt /requirements.txt

#RUN apt-get update
#RUN apt-get install -y postgresql-dev gcc python3-dev musl-dev
RUN pip install -r /requirements.txt

EXPOSE 5057

COPY ./app /app

CMD rm /app/uploads/*
CMD uvicorn app.main:app --host 0.0.0.0 --port 5057
