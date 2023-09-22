FROM python:3.10-slim-buster

# create directory for the app user

# create the app user


ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

WORKDIR /monkeygamestore
# # copy entrypoint.prod.sh

COPY rqworker.conf /etc/supervisor/conf.d/rqworker.conf
# # copy project
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./custom_django_file/registry.py /usr/local/lib/python3.10/site-packages/django/apps/




