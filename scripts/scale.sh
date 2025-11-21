#!/bin/bash
# Scale API containers for load testing

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scale.sh <number_of_replicas>"
    echo "Example: ./scale.sh 4"
    exit 1
fi

NUM_REPLICAS=$1

echo "🔄 Scaling API services to $NUM_REPLICAS replicas..."

docker-compose up -d --scale api=$NUM_REPLICAS --no-recreate

sleep 3

echo "✅ Scaled to $NUM_REPLICAS replicas"
echo ""
docker-compose ps | grep api
