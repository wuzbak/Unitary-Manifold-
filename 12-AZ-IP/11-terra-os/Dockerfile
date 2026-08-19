# TerraOS — Soil & Water Expert System — Docker Image
# Usage:
#   docker build -t terra-os .
#   docker run -p 8001:8001 --env-file .env terra-os
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="1.0"
LABEL description="TerraOS — Soil and Water Expert System"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
