#!/bin/bash
# Quick start script for local development

set -e

echo "🚀 Starting Cassava Leaf Disease MLOps Pipeline..."
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🎬 Starting services..."
docker-compose up -d

sleep 5

# Check services
echo ""
echo "✅ Services started!"
echo ""
echo "📡 API:        http://localhost/docs"
echo "💻 UI:         http://localhost:8501"
echo "📊 Nginx:      http://localhost"
echo ""
echo "Run load tests with:"
echo "  locust -f locustfile.py --host=http://localhost --users=100 --spawn-rate=10 --run-time=1m"
echo ""
echo "View logs:"
echo "  docker-compose logs -f api_1"
echo ""
echo "Stop services:"
echo "  docker-compose down"
