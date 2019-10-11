FROM python:3.6
RUN mkdir /django-docker
WORKDIR /django-docker
ADD requirements.txt /django-docker/
RUN pip install -r requirements.txt
ADD . /django-docker/