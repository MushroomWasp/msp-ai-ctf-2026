FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system ctf && adduser --system --ingroup ctf ctf

COPY pyproject.toml /app/pyproject.toml
COPY shared /app/shared
RUN pip install --no-cache-dir .

COPY challenges/08-atlas-analytics /app/challenge

USER ctf
EXPOSE 8108

CMD ["python3", "/app/challenge/app/backend/main.py"]
