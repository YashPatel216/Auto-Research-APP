FROM python:3.11-slim

WORKDIR /app

COPY requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]