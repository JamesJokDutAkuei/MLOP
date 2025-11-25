FROM python:3.10.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY deploy/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY src/ src/

# Expose port
EXPOSE 8000

# Run mock API
CMD ["uvicorn", "src.api_mock:app", "--host", "0.0.0.0", "--port", "8000"]
