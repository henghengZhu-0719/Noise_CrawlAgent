FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.10-slim-bookworm
WORKDIR /app
COPY requirements.txt pyproject.toml /app/
RUN pip install -r requirements.txt && \
    playwright install chromium --with-deps
COPY backend /app/backend
COPY crawl_service /app/crawl_service
COPY agent_service /app/agent_service
RUN pip install -e .
CMD ["python", "-m", "agent_service.main"]