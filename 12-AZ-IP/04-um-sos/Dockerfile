FROM python:3.12-slim

WORKDIR /app
COPY src /app/src
COPY docs /app/docs
COPY FALLIBILITY.md /app/FALLIBILITY.md
COPY 12-AZ-IP/04-um-sos /app/12-AZ-IP/04-um-sos
WORKDIR /app/12-AZ-IP/04-um-sos

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
ENV PYTHONPATH=/app
ENV UM_SOS_HOST=0.0.0.0
ENV UM_SOS_PREREGISTRATION_DB=/data/preregistrations.sqlite3
VOLUME ["/data"]
CMD ["python", "run.py"]
