FROM python:3.11

WORKDIR /app

COPY requirements.txt.lock /app/requirements.txt.lock

COPY embeddings_model/BAAI_bge-base-zh-v1.5 /app/embeddings_model/BAAI_bge-base-zh-v1.5

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt.lock

COPY gen_ai /app/gen_ai
COPY alembic.ini.docker /app/alembic.ini
COPY alembic /app/alembic

WORKDIR /app

CMD ["uvicorn", "gen_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
