FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV APP_PORT=5000
ENV LOG_FILE=/data/log
ENV OLLAMA_PROMPT_FILE=/data/prompt
ENV OLLAMA_MODEL_NAME=gemma2:2b
ENV OLLAMA_API_URL=http://ollama:11434/api/generate
ENV OLLAMA_TRUNCATE_NUMBER=200
ENV PAPERLESS_API_URL=http://paperless-ngx:8000/api
ENV PAPERLESS_API_TOKEN=""

EXPOSE $APP_PORT

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $APP_PORT"]
