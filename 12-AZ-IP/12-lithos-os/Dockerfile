# LithosOS — Mineral & Gemstone Identifier — Docker Image
# Usage:
#   docker build -t lithos-os .
#   docker run -p 7861:7861 -v $(pwd)/data:/app/data lithos-os
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="1.0"
LABEL description="LithosOS — Mineral and Gemstone Identifier"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
EXPOSE 7861
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "7861"]
