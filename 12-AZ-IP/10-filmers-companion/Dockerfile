# FilmersCompanion — Desktop Server Docker Image
# Usage:
#   docker build -t filmers-companion .
#   docker run -p 7864:7864 -v $(pwd)/data:/app/data filmers-companion
FROM python:3.12-slim
LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="1.0.0"
LABEL description="FilmersCompanion — AI Film Production Suite"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
EXPOSE 7864
CMD ["python", "-m", "desktop.app.main"]
