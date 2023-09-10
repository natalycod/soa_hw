FROM python:3.8 as builder

RUN pip3 install grpcio grpcio-tools

WORKDIR /mafia

RUN pip install --upgrade pip
RUN pip install requests

COPY rest_client.py ./

ENTRYPOINT [ "python3", "rest_client.py" ]