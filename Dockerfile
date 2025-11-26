FROM python:3.10.13-slim

WORKDIR /app

# Copy requirements first
COPY ./deploy/requirements.txt requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libstdc++6 ca-certificates && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --only-binary=:all:

# Copy source code
COPY ./src ./src

# Copy models (includes .h5 and .tflite if present)
COPY ./models ./models

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "src.api_tflite:app", "--host", "0.0.0.0", "--port", "8000"]
