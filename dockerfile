FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt
RUN pipi intall --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]