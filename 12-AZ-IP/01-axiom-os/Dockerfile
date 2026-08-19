# AXIOM OS — AI Operating System — Docker Image
# Usage:
#   docker-compose up --build
# Or standalone:
#   docker build -t axiom-os .
#   docker run -p 7900:7900 -p 7901:7901 axiom-os
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="0.1.0"
LABEL description="AXIOM OS — AxiomZero AI Operating System"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data memory
EXPOSE 7900 7901
CMD ["python", "axiomzero_bootstrap.py"]
