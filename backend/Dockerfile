FROM python:3.8.5

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

CMD [ "gunicorn", "--bind", "0.0.0.0:80", "app:app"]