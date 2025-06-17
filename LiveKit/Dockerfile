FROM python:3.10-slim
WORKDIR /app
COPY LiveKit/LivekitWorker.py LiveKit/context_manager.py LiveKit/superAgent.py LiveKit/RAGer.py LiveKit/LogMetrics.py ./
COPY LiveKit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p ./vector_db
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "LivekitWorker.py", "start"]
