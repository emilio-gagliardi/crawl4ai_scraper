FROM python:3.11-slim

WORKDIR /app

COPY frontend /app/frontend
COPY requirements.txt /app/

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "frontend/app.py"]
