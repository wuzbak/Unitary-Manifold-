FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastapi uvicorn[standard] numpy scipy sympy mpmath

EXPOSE 8000
CMD ["uvicorn", "src.core.um_sos_backend:app", "--host", "0.0.0.0", "--port", "8000"]
