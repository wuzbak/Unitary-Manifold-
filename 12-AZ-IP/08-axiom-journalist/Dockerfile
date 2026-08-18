# AXIOM Investigative Journalist AI — Docker Image
# Usage:
#   docker build -t axiom-journalist .
#   docker run -p 7870:7870 -v $(pwd)/data:/app/data axiom-journalist
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="1.0"
LABEL description="AXIOM Investigative Journalist AI"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
EXPOSE 7870
CMD ["python", "run.py"]
