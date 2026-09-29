FROM python:3.12-slim

WORKDIR /app

COPY app/app.py .

RUN useradd -m appuser

USER appuser

CMD ["python", "app.py"]