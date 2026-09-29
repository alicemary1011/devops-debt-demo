FROM python:latest

WORKDIR /app

COPY app/app.py .

RUN useradd -m appuser

USER appuser

CMD ["python", "app.py"]