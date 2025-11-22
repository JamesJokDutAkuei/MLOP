#!/usr/bin/env python3
"""Quick API smoke test"""
import requests, sys, time
from pathlib import Path

API = "http://127.0.0.1:8000"

def main():
    image = sys.argv[1] if len(sys.argv) > 1 else None
    print("\n=== Brain Tumor MRI Classifier API - Smoke Test ===\n")
    
    try:
        # Test 1: Health
        print("[1] GET /health")
        r = requests.get(f"{API}/health", timeout=5)
        r.raise_for_status()
        h = r.json()
        print(f"    ✓ Status: {h['status']}, Model: {h['model_loaded']}, Uptime: {h['uptime_seconds']}s")
        
        # Test 2: Predict
        if image and Path(image).exists():
            print(f"\n[2] POST /predict ({Path(image).name})")
            with open(image, 'rb') as f:
                r = requests.post(f"{API}/predict", files={'file': f}, timeout=30)
            r.raise_for_status()
            p = r.json()
            print(f"    ✓ Prediction: {p['predicted_class_short']}")
            print(f"    ✓ Confidence: {p['confidence']:.2%}")
            print(f"    ✓ Inference: {p['inference_time_ms']:.0f}ms")
            print(f"    ✓ Probabilities: {p['probabilities']}")
        else:
            print(f"\n[2] POST /predict (skipped, no test image)")
        
        # Test 3: Retrain
        print(f"\n[3] POST /retrain")
        r = requests.post(f"{API}/retrain", json={"epochs":1}, timeout=5)
        r.raise_for_status()
        job = r.json()
        print(f"    ✓ Job: {job['job_id']}")
        print(f"    ✓ Status: {job['status']}")
        
        # Test 4: Retrain status
        print(f"\n[4] GET /retrain_status")
        time.sleep(0.5)
        r = requests.get(f"{API}/retrain_status/{job['job_id']}", timeout=5)
        r.raise_for_status()
        s = r.json()
        print(f"    ✓ Status: {s['status']}")
        
        # Test 5: Retrain jobs list
        print(f"\n[5] GET /retrain_jobs")
        r = requests.get(f"{API}/retrain_jobs", timeout=5)
        r.raise_for_status()
        jobs = r.json()
        print(f"    ✓ Total jobs tracked: {jobs['total_jobs']}")
        
        print("\n" + "="*50)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*50 + "\n")
        return 0
        
    except requests.exceptions.ConnectionError:
        print(f"\n✗ FAILED: Cannot connect to {API}")
        print("\nStart the API server first:")
        print("  cd /Users/apple/MLOP")
        print("  python src/api.py\n")
        return 1
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {e}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
