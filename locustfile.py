"""
Locust Load Testing Script for Cassava Leaf Disease API

Simulates concurrent users making predictions to test:
- Response time
- Throughput
- Latency under load
- Error rates
"""

import random
import time
from io import BytesIO
from locust import HttpUser, task, between, events
import csv
from datetime import datetime
from pathlib import Path

# Create test image (1x1 white pixel PNG)
TEST_IMAGE = BytesIO(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
    b'\x00\x01\x01\x00\x051\xc3c\xce\x00\x00\x00\x00IEND\xaeB`\x82'
)

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


class CassavaAPIUser(HttpUser):
    """Locust user for Cassava API load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Run at start of test."""
        pass
    
    @task(3)
    def predict_image(self):
        """Task: Make prediction on image."""
        TEST_IMAGE.seek(0)
        
        with self.client.post(
            '/predict',
            files={'file': ('test.png', TEST_IMAGE, 'image/png')},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                results['success_count'] += 1
                response.success()
            else:
                results['error_count'] += 1
                response.failure(f"Status {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Task: Check API health."""
        with self.client.get('/health', catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


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
