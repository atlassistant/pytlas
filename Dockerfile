FROM python:3.6-slim

COPY . /src

WORKDIR /src

RUN pip install -e ".[snips]"

VOLUME [ "/pytlas" ]
WORKDIR /pytlas

ENTRYPOINT [ "pytlas", "-v" ]