import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.detection.inference import load_model, run_inference_with_geo
from src.geolocation.defaults import TEST_PARAMS
from src.geolocation.export import detections_to_geojson

# Model path — worker loads its own model instance
MODEL_PATH = "models/finetuned/visdrone_v1/weights/best.pt"


def run_detection_job(image_path: str, conf_threshold: float = 0.25) -> dict:
    """
    The actual detection work that runs inside the worker process.
    This function is what gets enqueued and executed by RQ.

    Accepts an image path, runs the full pipeline,
    returns a serializable result dict.
    """
    print(f"Worker processing: {image_path}")

    # Load model — each worker process has its own model instance
    model = load_model(MODEL_PATH)

    # Run detection and geolocation
    result = run_inference_with_geo(
        model,
        image_path,
        TEST_PARAMS,
        conf_threshold=conf_threshold
    )

    # Build the geojson
    geojson = detections_to_geojson(
        result["geo_detections"],
        metadata={"image_path": image_path}
    )

    # Return only serializable data — no numpy arrays or cv2 objects
    return {
        "image_path": image_path,
        "total_detections": result["count"],
        "detections": result["geo_detections"],
        "geojson": geojson
    }