FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY frontend /app/frontend

EXPOSE 8502

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8502", "--server.address=0.0.0.0"] 