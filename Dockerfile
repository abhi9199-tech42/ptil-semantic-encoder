FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY ptil/ ptil/

RUN pip install --no-cache-dir ".[server]" \
    && python -m spacy download en_core_web_sm

EXPOSE 8000

CMD ["ptil", "serve", "--host", "0.0.0.0", "--port", "8000"]
