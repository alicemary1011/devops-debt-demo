FROM python:3.12-slim

WORKDIR /project

COPY analyzer.py .
COPY terraform/ ./terraform/
COPY .github/ ./.github/

RUN useradd -m appuser && chown -R appuser:appuser /project

USER appuser

CMD ["python", "analyzer.py"]