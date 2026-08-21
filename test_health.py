from fastapi.testclient import TestClient
from app.main import app
import logging
logging.basicConfig(level=logging.INFO)

print("Starting test...")
with TestClient(app) as client:
    print("Testing /health")
    response = client.get("/health")
    print(response.status_code)
    print(response.json())
