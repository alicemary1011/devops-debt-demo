FROM python:3.12-slim

WORKDIR /project

# Install API dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy analyzer and project configuration
COPY analyzer.py .
COPY api.py .
COPY Dockerfile .
COPY terraform/ ./terraform/
COPY .github/ ./.github/

# Create non-root user and give it ownership of the project
RUN useradd -m appuser && chown -R appuser:appuser /project

USER appuser

# Start the FastAPI server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]