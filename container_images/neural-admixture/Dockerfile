FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --prefix=/install neural-admixture==1.6.7

# Final image
FROM python:3.12-slim

COPY --from=builder /install /usr/local

WORKDIR /workspace

CMD ["python"]
