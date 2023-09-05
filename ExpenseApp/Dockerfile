# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN apt-get update
RUN pip install -r requirements.txt

CMD ["python", "app.py"]