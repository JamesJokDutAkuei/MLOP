# 📊 Load Testing Guide - Brain Tumor MRI Classifier

This guide covers running load tests using Locust to benchmark your API performance.

---

## 📋 Prerequisites

```bash
# Install Locust
pip install locust==2.15.1

# Verify installation
locust --version
```

---

## 🚀 Quick Start

### 1. Start your API & UI

**Terminal 1 - API:**
```bash
cd /Users/apple/MLOP
/opt/homebrew/bin/docker-compose up -d
```

**Terminal 2 - Verify API is running:**
```bash
curl http://localhost/health
```

---

## 🧪 Load Testing Scenarios

### Scenario 1: Basic Performance Test (5 users, 1 minute)

```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=5 \
  --spawn-rate=1 \
  --run-time=1m \
  --headless \
  --csv=logs/locust_results/basic
```

**Expected Results:**
- Response time: < 500ms
- Success rate: > 99%
- RPS: 5-10 requests/second

---

### Scenario 2: Medium Load Test (50 users, 5 minutes)

```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless \
  --csv=logs/locust_results/medium
```

**Expected Results:**
- Avg Response time: 200-800ms
- Success rate: > 98%
- RPS: 20-50 requests/second

---

### Scenario 3: High Load Test (100+ users, 10 minutes)

```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=100 \
  --spawn-rate=10 \
  --run-time=10m \
  --headless \
  --csv=logs/locust_results/high_load
```

**Expected Results:**
- Avg Response time: 500-1500ms
- Success rate: > 95%
- Max concurrent users: ~100

---

### Scenario 4: Stress Test (Ramp up to failure)

```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=500 \
  --spawn-rate=50 \
  --run-time=15m \
  --headless \
  --csv=logs/locust_results/stress
```

**Measures:** Maximum sustainable load

---

## 🖥️ Interactive Web UI

Run Locust with web UI (no `--headless`):

```bash
locust -f locustfile.py --host=http://localhost
```

Then open http://localhost:8089 in your browser:
- Set number of users
- Set spawn rate
- Watch real-time graphs
- See response times, RPS, failure rates

---

## 📈 Analyzing Results

### CSV Results Files

After each test, Locust generates three CSVs:

1. **stats.csv** - Response statistics
```
Type,Name,# requests,# failures,Median response time,Average response time,Min response time,Max response time,Average Content Length,Requests/s
GET,/health,100,0,10,15,5,50,123,50
POST,/predict,50,1,450,520,200,1200,456,25
```

2. **failures.csv** - Failed requests
```
Method,Name,# failures,Failure message
POST,/predict,5,Connection timeout
```

3. **requests.csv** - Detailed per-request stats
```
Timestamp,Method,Name,Response time (ms),Bytes sent,Bytes received
1700000000,GET,/health,12,0,100
1700000001,POST,/predict,520,5000,1000
```

### Parse Results

```bash
# View stats
cat logs/locust_results/basic_stats.csv | column -t -s,

# Calculate percentiles
python3 << 'EOF'
import pandas as pd
stats = pd.read_csv('logs/locust_results/basic_stats.csv')
print("Response Time Percentiles:")
print(f"  50th percentile: {stats['Median response time'].median()}ms")
print(f"  Average: {stats['Average response time'].mean()}ms")
print(f"  Max: {stats['Max response time'].max()}ms")
print(f"Success rate: {100 - (stats['# failures'].sum() / stats['# requests'].sum() * 100):.2f}%")
EOF
```

---

## 🔍 Key Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|-----------|------|
| **Response Time (p50)** | < 200ms | 200-500ms | > 500ms |
| **Response Time (p95)** | < 500ms | 500-1000ms | > 1000ms |
| **Response Time (p99)** | < 1000ms | 1000-2000ms | > 2000ms |
| **Error Rate** | < 0.1% | 0.1-1% | > 1% |
| **Throughput** | > 100 RPS | 50-100 RPS | < 50 RPS |

---

## 📊 Example Report

```
Load Test Results - Brain Tumor MRI Classifier
================================================

Test Configuration:
- Duration: 5 minutes
- Peak Users: 50
- Spawn Rate: 5 users/sec

Results:
- Total Requests: 5,000
- Failed: 12 (0.24%)
- Passed: 4,988 (99.76%)

Response Times:
- Min: 45ms
- Median: 180ms
- Average: 245ms
- 95th percentile: 520ms
- 99th percentile: 890ms
- Max: 2,150ms

Throughput:
- Requests/sec: 16.7
- Bandwidth: 2.3 MB/sec

API Endpoints Performance:
- GET /health: Median 12ms (avg 15ms)
- POST /predict: Median 450ms (avg 520ms)
- GET /retrain_jobs: Median 25ms (avg 30ms)
- POST /retrain: Median 40ms (avg 45ms)

Scaling Analysis:
- 10 users: 98% success, avg 150ms
- 25 users: 97% success, avg 220ms
- 50 users: 97% success, avg 320ms
- 100 users: 95% success, avg 680ms
```

---

## 🎯 Performance Optimization Tips

If response times are high:

1. **Add API replicas**
```bash
docker-compose up -d --scale api=5
```

2. **Increase container resources**
```yaml
# In docker-compose.yml
resources:
  limits:
    cpus: '2'
    memory: 4G
```

3. **Enable caching**
```python
# In API code
from functools import lru_cache
@lru_cache(maxsize=128)
def load_model():
    return tf.keras.models.load_model('model.h5')
```

4. **Use database connection pooling**
5. **Profile code with Python profiler**

---

## 🚀 Continuous Load Testing

### Run daily tests

```bash
#!/bin/bash
# run_daily_tests.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="logs/locust_results/$TIMESTAMP"
mkdir -p $RESULTS_DIR

locust -f locustfile.py \
  --host=http://localhost \
  --users=50 \
  --spawn-rate=5 \
  --run-time=10m \
  --headless \
  --csv="$RESULTS_DIR/test"

echo "Test completed: $RESULTS_DIR"
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * cd /Users/apple/MLOP && bash run_daily_tests.sh
```

---

## 📝 Custom Load Scenarios

Edit `locustfile.py` to add custom scenarios:

```python
class CustomUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(5)
    def high_volume_predictions(self):
        """Heavy prediction load"""
        for _ in range(10):
            self.client.post("/predict", 
                files={'file': ('test.jpg', b'data', 'image/jpeg')})
    
    @task(1)
    def retrain_workflow(self):
        """Complete retrain workflow"""
        # Upload files
        self.client.post("/upload_training_data?label=glioma",
            files={'files': [('img1.jpg', b'data1'), ('img2.jpg', b'data2')]})
        
        # Start retrain
        self.client.post("/retrain", json={
            "epochs": 5,
            "batch_size": 32,
            "learning_rate": 1e-4
        })
        
        # Check status
        self.client.get("/retrain_jobs")
```

---

## ✅ Load Testing Checklist

- [ ] Locust installed
- [ ] API running and responding
- [ ] Test images available or mocked
- [ ] Results directory created
- [ ] Run quick test (5 users, 1 min)
- [ ] Run medium test (50 users, 5 min)
- [ ] Run high load test (100 users, 10 min)
- [ ] Analyze results
- [ ] Optimize if needed
- [ ] Document findings

---

## 📞 Troubleshooting

**High Response Times:**
- Check CPU/memory usage: `docker stats`
- Check API logs: `docker-compose logs api_1`
- Increase replicas or resources

**Failed Requests:**
- Check error logs for details
- Verify API health: `curl http://localhost/health`
- Check network connectivity

**Out of Memory:**
- Reduce number of concurrent users
- Check for memory leaks in API
- Increase Docker container memory

---

**Load testing helps ensure your API is production-ready!** 🚀
