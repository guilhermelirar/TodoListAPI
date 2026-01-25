FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["bash", "-c", "flask db upgrade && python run.py"]
