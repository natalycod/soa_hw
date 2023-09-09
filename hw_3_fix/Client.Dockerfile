FROM python:3.8 as builder

RUN pip3 install grpcio grpcio-tools

WORKDIR /mafia

COPY mafia.proto ./

RUN python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mafia.proto
RUN pip install --upgrade pip
RUN pip install pika

COPY client.py ./

ENTRYPOINT [ "python3", "client.py" ]