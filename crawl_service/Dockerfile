FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt pyproject.toml /app/
RUN pip install -r requirements.txt
COPY backend /app/backend
COPY crawl_service /app/crawl_service
CMD ["python", "-m", "crawl_service.main"]