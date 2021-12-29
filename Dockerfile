FROM python:3.9.9-slim-buster

WORKDIR /app

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8

RUN apt-get update
RUN apt-get install -y g++

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "run.py