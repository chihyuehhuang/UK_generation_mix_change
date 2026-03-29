FROM python:3.12-slim

WORKDIR /app

COPY deploy/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

COPY .streamlit/ ./.streamlit/

COPY deploy/app.py .

# ingest data into db
COPY deploy/entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["./entrypoint.sh"]
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]