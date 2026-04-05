FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

COPY app.py .

COPY templates/ ./templates/
COPY static/ ./static/

# ingest data into db
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
# CMD ["python", "app.py"]


CMD ["gunicorn", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:8080", "app:app"]
