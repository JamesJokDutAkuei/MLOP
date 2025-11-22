# 🐳 Docker Deployment Guide

## Quick Start

### 1. **Prerequisites**
- Docker installed ([Download Docker Desktop](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)
- 2GB free disk space for images
- macOS: Ensure Docker Desktop is running

### 2. **Start All Services**

```bash
cd /Users/apple/MLOP
docker-compose up --build
```

This starts:
- **Nginx Load Balancer** on http://localhost:80
- **API Container 1** on port 8001
- **API Container 2** on port 8002
- **Streamlit UI** on http://localhost:8501

### 3. **Access the Services**

| Service | URL |
|---------|-----|
| **Web UI** | http://localhost:8501 |
| **API via Nginx** | http://localhost:80 |
| **API 1 Direct** | http://localhost:8001 |
| **API 2 Direct** | http://localhost:8002 |
| **API Docs** | http://localhost:80/docs |
| **Nginx Health** | http://localhost:80/health |

---

## 🛠️ Docker Commands

### Start Services (Foreground)
```bash
docker-compose up
```

### Start Services (Background)
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api_1
docker-compose logs ui
docker-compose logs nginx

# Real-time logs
docker-compose logs -f api_1
```

### Scale API Services
```bash
# Run 4 API containers
docker-compose up -d --scale api_1=4

# Reset to 2
docker-compose down
docker-compose up -d
```

### Rebuild Images
```bash
docker-compose build --no-cache
```

### Remove Everything
```bash
docker-compose down -v  # -v removes volumes too
docker system prune -a  # Remove all unused images
```

---

## 📊 Service Architecture

```
┌─────────────────────────────────────────┐
│         Browser / Client                 │
└──────────────┬──────────────────────────┘
               │ http://localhost:80 or :8501
               │
      ┌────────▼────────┐
      │     Nginx       │ (Load Balancer)
      └────┬───────────┘
           │ Least Connection
           │
      ┌────┴─────────────┐
      │                  │
   ┌──▼────┐         ┌──▼────┐
   │ API 1  │         │ API 2  │ (Mock API)
   └────────┘         └────────┘
   Port 8001           Port 8002
   
   ┌──────────────┐
   │  Streamlit   │ UI
   │     UI       │
   └──────────────┘
   Port 8501
```

---

## ✅ Health Checks

The services have built-in health checks:

```bash
# Check Nginx health
curl http://localhost/health

# Check API 1 health
curl http://localhost:8001/health

# Check API 2 health
curl http://localhost:8002/health
```

Example response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1",
  "uptime_seconds": 123
}
```

---

## 🧪 Testing the Deployment

### 1. **Test Prediction via Nginx (Load Balanced)**
```bash
curl -X POST "http://localhost/predict" \
  -F "file=@/path/to/image.jpg"
```

### 2. **Test UI**
Open browser: http://localhost:8501

Upload an MRI image → Should show prediction results

### 3. **View API Documentation**
Open browser: http://localhost/docs

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process using port 80
lsof -i :80

# Kill it
kill -9 <PID>

# Or use different port in docker-compose.yml
# Change "80:80" to "8080:80"
```

### Container Won't Start
```bash
# Check logs
docker-compose logs api_1

# Rebuild
docker-compose build --no-cache api_1

# Restart
docker-compose restart api_1
```

### Low Disk Space
```bash
# Clean up Docker system
docker system prune -a --volumes
```

### Nginx can't reach API
```bash
# Ensure containers are in same network
docker network inspect mlop_cassava_network

# Restart all
docker-compose down
docker-compose up -d
```

---

## 📈 Monitoring

### View Container Stats
```bash
docker stats

# Real-time CPU/Memory usage
```

### View Container Logs with Timestamps
```bash
docker-compose logs --timestamps api_1
```

### Check Container Status
```bash
docker-compose ps
```

Expected output:
```
NAME               STATUS           PORTS
cassava_nginx      Up (healthy)     0.0.0.0:80->80/tcp
cassava_api_1      Up (healthy)     0.0.0.0:8001->8000/tcp
cassava_api_2      Up (healthy)     0.0.0.0:8002->8000/tcp
cassava_ui         Up               0.0.0.0:8501->8501/tcp
```

---

## 🚀 Production Tips

### 1. Use Specific Image Tags
Edit `docker-compose.yml`:
```yaml
api_1:
  image: mlop-api:v1.0.0  # Instead of 'latest'
```

### 2. Increase Resource Limits
```yaml
services:
  api_1:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### 3. Enable HTTPS
Update nginx.conf with SSL certificates

### 4. Add Environment Variables
```yaml
environment:
  - LOG_LEVEL=INFO
  - MODEL_VERSION=v2
```

### 5. Use Named Volumes for Data Persistence
```yaml
volumes:
  model_cache:
  training_logs:

services:
  api_1:
    volumes:
      - model_cache:/app/models
      - training_logs:/app/logs
```

---

## 📝 Docker Files Reference

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Defines all services and networking |
| `deploy/Dockerfile.api` | API service image definition |
| `deploy/Dockerfile.ui` | Streamlit UI image definition |
| `deploy/nginx.conf` | Nginx reverse proxy config |

---

## ✨ What's Running in Docker

- **Nginx**: Acts as load balancer, routes requests to API containers
- **API Containers**: Mock API that simulates predictions (Python 3.11-slim)
- **Streamlit UI**: Web interface for predictions and retraining
- **Network**: All containers on same bridge network for communication

---

**Status**: ✅ Ready for Deployment!

For questions or issues, check the logs:
```bash
docker-compose logs -f
```
