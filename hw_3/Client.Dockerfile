FROM python:3.8 as builder

RUN pip3 install grpcio grpcio-tools

WORKDIR /chat_server

COPY mafia.proto ./

RUN python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mafia.proto

COPY client.py ./

ENTRYPOINT [ "python3", "client.py" ]