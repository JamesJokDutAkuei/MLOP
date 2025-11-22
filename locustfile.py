"""
Locust Load Testing Script for Brain Tumor MRI Classifier API

Simulates concurrent users making predictions to test:
- Response time (latency)
- Throughput (requests/second)
- Error rates under load
- System behavior with multiple replicas

Usage:
    locust -f locustfile.py --host=http://localhost:80 --users=100 --spawn-rate=10 --run-time=1m
    
Headless mode:
    locust -f locustfile.py --host=http://localhost:80 --users=100 --spawn-rate=10 --run-time=1m --headless

Web UI:
    locust -f locustfile.py --host=http://localhost:80
    Then open: http://localhost:8089
"""

import random
import time
import os
from io import BytesIO
from locust import HttpUser, task, between, events
import csv
from datetime import datetime
from pathlib import Path

# Test images
TEST_IMAGES = {
    'tumor_glioma': (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x051\xc3c\xce\x00\x00\x00\x00IEND\xaeB`\x82'
    ),
    'tumor_meningioma': (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x051\xc3c\xce\x00\x00\x00\x00IEND\xaeB`\x82'
    ),
    'tumor_pituitary': (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x051\xc3c\xce\x00\x00\x00\x00IEND\xaeB`\x82'
    ),
    'no_tumor': (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x051\xc3c\xce\x00\x00\x00\x00IEND\xaeB`\x82'
    )
}

# Results storage
results = {
    'response_times': [],
    'success_count': 0,
    'error_count': 0,
    'start_time': datetime.now()
}

# Configure logging
LOGS_DIR = Path('logs/locust_results')
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# CSV writer for results
results_file = LOGS_DIR / f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
csv_writer = None


class BrainTumorAPIUser(HttpUser):
    """Locust user for Brain Tumor MRI API load testing.
    
    Simulates realistic users:
    - 60% make predictions (most common)
    - 20% check health
    - 20% trigger retraining
    """
    
    wait_time = between(1, 4)  # Wait 1-4 seconds between requests
    
    def on_start(self):
        """Run at start of each user's test."""
        pass
    
    @task(6)
    def predict_image(self):
        """Task: Make prediction on MRI image (60% of traffic)."""
        # Select random test image
        image_class = random.choice(list(TEST_IMAGES.keys()))
        image_data = TEST_IMAGES[image_class]
        
        with self.client.post(
            '/predict',
            files={'file': ('test.png', BytesIO(image_data), 'image/png')},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                results['success_count'] += 1
                response.success()
            else:
                results['error_count'] += 1
                response.failure(f"Prediction failed: {response.status_code}")
    
    @task(2)
    def health_check(self):
        """Task: Check API health (20% of traffic)."""
        with self.client.get('/health', catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def retrain_trigger(self):
        """Task: Trigger model retraining (20% of traffic)."""
        payload = {
            'epochs': random.randint(1, 10),
            'batch_size': random.choice([8, 16, 32, 64]),
            'learning_rate': random.choice([1e-3, 1e-4, 1e-5])
        }
        
        with self.client.post('/retrain', json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Retrain failed: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    results['start_time'] = datetime.now()
    print("\n" + "="*70)
    print("LOCUST LOAD TEST STARTED")
    print("="*70)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    end_time = datetime.now()
    duration = (end_time - results['start_time']).total_seconds()
    
    # Get stats from locust
    stats = environment.stats
    total_requests = sum(s.num_requests for s in stats.entries.values())
    total_failures = sum(s.num_failures for s in stats.entries.values())
    
    # Calculate throughput
    throughput = total_requests / duration if duration > 0 else 0
    
    # Response time stats
    response_times = []
    for entry in stats.entries.values():
        if hasattr(entry, 'response_times'):
            response_times.extend(entry.response_times.values())
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Print results
    print("\n" + "="*70)
    print("LOAD TEST RESULTS")
    print("="*70)
    print(f"Test Duration:        {duration:.2f}s")
    print(f"Total Requests:       {total_requests}")
    print(f"Successful:           {total_requests - total_failures}")
    print(f"Failed:               {total_failures}")
    print(f"Success Rate:         {((total_requests - total_failures) / total_requests * 100):.2f}%" if total_requests > 0 else "N/A")
    print(f"Throughput:           {throughput:.2f} req/s")
    print(f"Avg Response Time:    {avg_response_time:.2f}ms")
    print("="*70)
    
    # Save results to CSV
    save_results(environment, duration, throughput)


def save_results(environment, duration, throughput):
    """Save test results to CSV."""
    stats = environment.stats
    
    csv_path = LOGS_DIR / f'load_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write summary
        writer.writerow(['Load Test Summary'])
        writer.writerow(['Test Duration (s)', duration])
        writer.writerow(['Throughput (req/s)', throughput])
        writer.writerow([])
        
        # Write per-endpoint stats
        writer.writerow(['Endpoint', 'Method', 'Requests', 'Failures', 'Avg Response (ms)', 'Min (ms)', 'Max (ms)'])
        
        for entry in stats.entries.values():
            if entry.name != 'Total':
                avg_resp = entry.avg_response_time if hasattr(entry, 'avg_response_time') else 'N/A'
                writer.writerow([
                    entry.name,
                    entry.method,
                    entry.num_requests,
                    entry.num_failures,
                    f"{avg_resp:.2f}" if isinstance(avg_resp, (int, float)) else avg_resp,
                    f"{entry.min_response_time:.2f}" if hasattr(entry, 'min_response_time') else 'N/A',
                    f"{entry.max_response_time:.2f}" if hasattr(entry, 'max_response_time') else 'N/A'
                ])
    
    print(f"\n✓ Results saved to {csv_path}")


if __name__ == '__main__':
    print("""
    Run load test with:
    locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=1m
    
    Or for more containers:
    locust -f locustfile.py --host=http://localhost:80 --users=200 --spawn-rate=20 --run-time=2m
    """)
