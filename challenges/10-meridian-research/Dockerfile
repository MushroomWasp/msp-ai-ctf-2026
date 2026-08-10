FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system ctf && adduser --system --ingroup ctf ctf

COPY pyproject.toml /app/pyproject.toml
COPY shared /app/shared
COPY challenges/10-meridian-research /app/challenge

RUN pip install .

USER ctf
EXPOSE 8110

CMD ["python3", "/app/challenge/app/backend/main.py"]
