FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

COPY ./compose/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

CMD ['gunicorn', '--bind', '0.0.0.0:8000', 'table_builder.wsgi:application']
