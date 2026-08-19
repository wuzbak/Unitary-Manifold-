# OmegaHolon Living Systems Engine — Docker Image
# Usage:
#   docker build -t omegaholon .
#   docker run -p 7871:7871 -v $(pwd)/data:/app/data omegaholon
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="1.0"
LABEL description="OmegaHolon — Living Systems Engine"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
EXPOSE 7871
CMD ["python", "run.py"]
