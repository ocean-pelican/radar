import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import random

BASE_URL = "http://localhost:8000/api/v1"
VAL_IMAGES = Path("data/processed/VisDrone2019-DET/VisDrone2019-DET-val/images")


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    print("✓ Health check passed")


def test_detect():
    images = list(VAL_IMAGES.glob("*.jpg"))
    img_path = random.choice(images)

    with open(img_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/detect",
            files={"file": (img_path.name, f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "detections" in data
    assert "geojson" in data
    assert data["total_detections"] == len(data["detections"])
    print(f"✓ Detection passed — {data['total_detections']} detections in {img_path.name}")


def test_geojson():
    images = list(VAL_IMAGES.glob("*.jpg"))
    img_path = random.choice(images)

    with open(img_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/detect/geojson",
            files={"file": (img_path.name, f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    print(f"✓ GeoJSON passed — {len(data['features'])} features returned")


if __name__ == "__main__":
    print("Running API tests — make sure the server is running first.\n")
    test_health()
    test_detect()
    test_geojson()
    print("\nAll tests passed.")