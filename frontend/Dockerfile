FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
# Configuration Streamlit pour Docker
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]