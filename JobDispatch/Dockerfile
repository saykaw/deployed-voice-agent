FROM python:3.10-slim

WORKDIR /app

COPY JobDispatch/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY JobDispatch/* . 

RUN mkdir -p ./vector_db
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
