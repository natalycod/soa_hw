FROM python:3.8 as builder

RUN pip3 install grpcio grpcio-tools

WORKDIR /mafia

COPY mafia.proto ./
COPY pdfs ./

RUN python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mafia.proto
RUN pip install --upgrade pip
RUN pip install pika
RUN pip install flask
RUN pip install fpdf
RUN pip install flask_sqlalchemy

COPY server.py ./

ENTRYPOINT [ "python3", "server.py" ]