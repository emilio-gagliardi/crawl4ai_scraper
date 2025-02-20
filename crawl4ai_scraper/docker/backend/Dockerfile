FROM python:3.9

WORKDIR /app

COPY backend /app/backend
COPY requirements.txt /app/
COPY config.yaml /app/

RUN pip install -r requirements.txt
RUN pip install crawl4ai
RUN crawl4ai-setup

CMD ["python", "backend/main.py"]
