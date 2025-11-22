# 🐳 Docker Installation & Deployment Complete Guide

## Step 1: Install Docker Desktop

### macOS Installation

1. **Download Docker Desktop for Mac**
   - Visit: https://www.docker.com/products/docker-desktop
   - Choose: **Apple Silicon (M1/M2/M3)** or **Intel**
   - Download the `.dmg` file

2. **Install Docker**
   - Open the downloaded `.dmg` file
   - Drag Docker icon to Applications folder
   - Wait for installation to complete

3. **Launch Docker**
   - Open Applications → Docker.app
   - Enter your Mac password when prompted
   - Wait for "Docker Desktop is running"

4. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   ```
   
   Expected output:
   ```
   Docker version 24.x.x, build xxxxx
   Docker Compose version 2.x.x
   ```

---

## Step 2: Pre-Build Checklist

Before building Docker images, ensure:

- [ ] Docker Desktop is running
- [ ] You have ~3GB free disk space
- [ ] You're in the project directory:
  ```bash
  cd /Users/apple/MLOP
  ```

---

## Step 3: Build Docker Images

### Quick Build
```bash
cd /Users/apple/MLOP
docker compose build --no-cache
```

### Expected Output
```
[+] Building 120.3s (45/45) FINISHED
 => [nginx internal] load build definition
 => [api_1 internal] load build definition
 => [ui internal] load build definition
 => exporting to image
 => => naming to mlop_api_1:latest
 => => naming to mlop_ui:latest
 ...
Successfully tagged mlop_nginx:latest
```

**Build Time**: ~2-3 minutes on first build

---

## Step 4: Start All Services

### Option A: Run in Foreground (See logs in real-time)
```bash
docker compose up
```

### Option B: Run in Background (Recommended)
```bash
docker compose up -d
```

### Verify Services Started
```bash
docker compose ps
```

Expected output:
```
NAME               COMMAND                  SERVICE     STATUS
mlop-nginx-1       "/docker-entrypoint.…"   nginx       Up (healthy)
mlop-api_1-1       "python src/api_mock.…"  api_1       Up (healthy)
mlop-api_2-1       "python src/api_mock.…"  api_2       Up (healthy)
mlop-ui-1          "streamlit run deploy…"  ui          Up
```

---

## Step 5: Access Services

Once all services are **UP** and **healthy**:

| Service | URL | Purpose |
|---------|-----|---------|
| **UI** | http://localhost:8501 | Web interface for predictions |
| **API via Nginx** | http://localhost:80 | Load-balanced API |
| **API Direct 1** | http://localhost:8001 | First API instance |
| **API Direct 2** | http://localhost:8002 | Second API instance |
| **API Docs** | http://localhost/docs | Swagger documentation |

---

## Step 6: Test Deployment

### Test 1: Check API Health
```bash
curl http://localhost/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1",
  "uptime_seconds": 45
}
```

### Test 2: Test Prediction via Load Balancer
```bash
curl -X POST "http://localhost/predict" \
  -F "file=@/path/to/brain_mri.jpg"
```

### Test 3: Access Streamlit UI
Open browser: http://localhost:8501

1. Go to **🔮 Predict** tab
2. Upload a brain MRI image
3. Click **"🚀 Predict"**
4. Should show prediction result and probability chart

---

## 🔍 Monitoring & Troubleshooting

### View Logs

**All services:**
```bash
docker compose logs
```

**Specific service:**
```bash
docker compose logs api_1      # First API
docker compose logs ui         # Streamlit UI
docker compose logs nginx      # Nginx load balancer
```

**Real-time logs:**
```bash
docker compose logs -f api_1   # Follow logs for API 1
```

### View Resource Usage
```bash
docker stats
```

Shows real-time CPU/Memory/Network for each container

### Check Container Details
```bash
docker compose ps -a           # All containers
docker ps                      # All running containers
docker inspect mlop-api_1-1    # Detailed info about container
```

---

## 🛠️ Common Docker Commands

### Stop Services
```bash
docker compose down              # Stop all, remove containers
docker compose pause             # Pause services
docker compose unpause           # Resume services
```

### Restart Services
```bash
docker compose restart           # Restart all services
docker compose restart api_1     # Restart specific service
```

### View Logs with Timestamps
```bash
docker compose logs --timestamps -f
```

### Remove Everything (Clean Slate)
```bash
docker compose down -v           # Remove volumes too
docker system prune -a           # Remove all unused images
```

### Scale Services
```bash
# Increase API containers to 4
docker compose up -d --scale api_1=4

# Reset to default (2 API + 1 UI + 1 Nginx)
docker compose down
docker compose up -d
```

---

## 🐛 Troubleshooting

### Issue: "docker: command not found"
**Solution**: Docker Desktop not installed
```bash
# Install from https://www.docker.com/products/docker-desktop
```

### Issue: "Port 80 already in use"
**Solution 1**: Stop other services
```bash
lsof -i :80
kill -9 <PID>
```

**Solution 2**: Use different port (edit docker-compose.yml)
```yaml
nginx:
  ports:
    - "8080:80"    # Use 8080 instead of 80
```

### Issue: "Service unhealthy"
**Solution**: Check logs
```bash
docker compose logs api_1
docker compose logs nginx
```

### Issue: Nginx can't reach API
**Solution**: Restart all services
```bash
docker compose down
docker compose up -d
```

### Issue: Out of Disk Space
**Solution**: Clean Docker system
```bash
docker system prune -a --volumes
docker image prune -a
```

### Issue: Changes not reflected
**Solution**: Rebuild images
```bash
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Architecture Diagram

```
Internet/Browser
     │
     ├─ http://localhost:8501  ──────────────┐
     │                                        │
     └─ http://localhost:80    ────────────────┼────┐
                                              │    │
                                    ┌─────────┴────┴──────────┐
                                    │     Docker Compose      │
                                    │    (mlop_network)       │
                                    │                         │
         ┌──────────────────────────┼─────────────────────┐  │
         │                          │                     │  │
    ┌────▼─────┐             ┌──────▼───────┐       ┌────▼──┴───┐
    │  Nginx   │             │   Streamlit  │       │  Missing  │
    │(LB:Port80)             │   UI:8501    │       │ depends   │
    └────┬─────┘             └──────────────┘       └───────────┘
         │
         ├─ Round-robin to API containers
         │
    ┌────┴────────────────────┐
    │                         │
┌──▼───────┐            ┌───▼──────┐
│  API 1   │            │  API 2   │
│ Port8001 │            │ Port8002 │
│(Mock API)│            │(Mock API)│
└──────────┘            └──────────┘

All containers share:
- Same network (mlop_network)
- Same volumes (models/, data/, logs/)
```

---

## 📈 Performance Tips

### 1. Increase Resource Allocation
In Docker Desktop preferences:
- Memory: 4GB+ recommended
- CPU: 2+ cores

### 2. Use BuildKit for Faster Builds
```bash
DOCKER_BUILDKIT=1 docker compose build --no-cache
```

### 3. Monitor Resources
```bash
docker stats --no-stream
```

### 4. Use Production Image
Update docker-compose.yml for production:
```yaml
api_1:
  image: mlop-api:v1.0.0-prod  # Use specific version
```

---

## ✅ Deployment Checklist

- [ ] Docker Desktop installed and running
- [ ] Images built successfully
- [ ] All services healthy
- [ ] API responds to health check
- [ ] UI accessible on port 8501
- [ ] Can upload image and get prediction
- [ ] Load balancer routing requests

---

## 🎓 Next Steps

1. **Test with real workloads**
   ```bash
   docker compose logs -f api_1
   ```

2. **Monitor performance**
   ```bash
   docker stats
   ```

3. **Scale if needed**
   ```bash
   docker compose up -d --scale api_1=4
   ```

4. **Deploy to production** (Google Cloud, AWS, etc.)
   - Push images to registry
   - Deploy using Kubernetes or Docker Swarm

---

## 📝 Docker Compose File Structure

Current setup in `docker-compose.yml`:

```yaml
version: '3.8'

services:
  nginx:        # Load balancer (port 80)
  api_1:        # API instance 1 (port 8001)
  api_2:        # API instance 2 (port 8002)
  ui:           # Streamlit UI (port 8501)

networks:
  cassava_network:  # Shared network

volumes:
  (none - using bind mounts)
```

---

## 🚀 Summary

✅ **Docker deployment setup complete!**

### Start the system:
```bash
cd /Users/apple/MLOP
docker compose up -d
```

### Access services:
- **UI**: http://localhost:8501
- **API**: http://localhost:80

### Monitor:
```bash
docker compose logs -f
docker stats
docker compose ps
```

### Stop:
```bash
docker compose down
```

---

**Status**: Ready for Docker deployment! 🎉

For support, check logs:
```bash
docker compose logs <service_name>
```
