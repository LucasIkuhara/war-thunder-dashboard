FROM python:latest

ENV DOCKER_DESKTOP=y

WORKDIR /wtd

COPY ./requirements.txt /wtd/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /wtd

EXPOSE 8000

WORKDIR /wtd/src

CMD ["python3", "-m", "uvicorn", "app:app"]
