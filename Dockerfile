#FROM python:3
#ENV PYTHONUNBUFFERED 1
#RUN mkdir /code
#WORKDIR /code
#ADD requirements.txt /code/
#RUN pip install -r requirements.txt
#ADD . /code/
FROM python:3.5.3-slim
RUN mkdir /django-rest-api
WORKDIR  /django-rest-api
ADD . /django-rest-api
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "./djangorest/manage.py", "runserver"]