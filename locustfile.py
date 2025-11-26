from locust import HttpUser, task, between
import os


SAMPLE_IMAGE = os.environ.get("SAMPLE_IMAGE", "data/test/No_Tumor/no_tumor_1.jpg")


class ApiUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task
    def predict(self):
        try:
            with open(SAMPLE_IMAGE, "rb") as f:
                files = {"file": (os.path.basename(SAMPLE_IMAGE), f, "image/jpeg")}
                self.client.post("/predict", files=files, name="predict")
        except FileNotFoundError:
            # Fallback to health if no image
            self.client.get("/health", name="health")
