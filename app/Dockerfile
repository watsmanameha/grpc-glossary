FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir grpcio grpcio-tools grpcio-reflection protobuf aiosqlite

COPY app /app/app
COPY protobufs /app/protobufs

# Компиляция .proto в папку /app/app/generated
RUN mkdir -p /app/app/generated && \
    python -m grpc_tools.protoc \
      -I/app/protobufs \
      --python_out=/app/app/generated \
      --grpc_python_out=/app/app/generated \
      /app/protobufs/glossary.proto && \
    touch /app/app/__init__.py /app/app/generated/__init__.py

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
EXPOSE 50051
CMD ["python", "-u", "-m", "app.server"]
