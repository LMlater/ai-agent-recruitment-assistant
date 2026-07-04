FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    LLM_PROVIDER=mock \
    LLM_ENABLE_REAL_API=false \
    REAL_API_ENABLED=false

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY knowledge_base ./knowledge_base
COPY models ./models

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
