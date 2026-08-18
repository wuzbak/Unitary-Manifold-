# DelPhi Oracle Suite — Docker Image
# Usage:
#   docker build -t delphi-oracle .
#   docker run -p 8080:8080 -v $(pwd)/data:/app/data delphi-oracle
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="1.0"
LABEL description="DelPhi — Oracle Divination Suite (Tarot, Runes, Astrology, Chinese Zodiac)"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
# Seed the divination database
RUN python -c "from app.db.seed import seed; seed()" 2>/dev/null || true
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
