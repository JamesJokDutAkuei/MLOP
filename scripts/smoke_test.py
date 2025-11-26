import argparse
import requests


def main():
    parser = argparse.ArgumentParser(description="Smoke test for Brain Tumor API")
    parser.add_argument("--api", required=True, help="API base URL, e.g. https://brain-tumor-api-x.onrender.com")
    parser.add_argument("--image", required=True, help="Path to a local image file")
    args = parser.parse_args()

    # Health
    h = requests.get(f"{args.api}/health", timeout=15)
    print("/health:", h.status_code, h.text[:200])
    h.raise_for_status()

    # Predict
    with open(args.image, "rb") as f:
        files = {"file": (args.image.split("/")[-1], f, "image/jpeg")}
        r = requests.post(f"{args.api}/predict", files=files, timeout=60)
    print("/predict:", r.status_code, r.text[:200])
    r.raise_for_status()
    data = r.json()

    required_keys = {"predicted_class", "confidence", "probabilities", "inference_time_ms"}
    missing = required_keys - set(data.keys())
    if missing:
        raise SystemExit(f"Missing keys in response: {missing}")
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
