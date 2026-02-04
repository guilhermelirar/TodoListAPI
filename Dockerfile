FROM python:3.11-slim

# RUN apt-get update && apt-get install -y \
#    libpq-dev \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py

# NADA de migrações aqui! Só a aplicação
CMD ["python", "run.py"]