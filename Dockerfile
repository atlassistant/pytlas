FROM python:3.6-slim

COPY . /src

WORKDIR /src

RUN pip install -e ".[snips]"
RUN snips-nlu download en

VOLUME [ "/pytlas" ]
WORKDIR /pytlas

ENTRYPOINT [ "pytlas", "-v" ]