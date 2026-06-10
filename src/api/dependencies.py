import os
from functools import lru_cache
from ultralytics import YOLO
from src.geolocation.defaults import TEST_PARAMS


# Default model path — can be overridden via environment variable
DEFAULT_WEIGHTS = os.getenv(
    "MODEL_WEIGHTS",
    "models/finetuned/visdrone_v1/weights/best.pt"
)


@lru_cache(maxsize=1)
def get_model() -> YOLO:
    """
    Load and cache the YOLO model.
    lru_cache ensures this only runs once — the model stays
    in memory for the lifetime of the server process.
    """
    print(f"Loading model from: {DEFAULT_WEIGHTS}")
    model = YOLO(DEFAULT_WEIGHTS)
    print("Model loaded and cached.")
    return model


def get_camera_params():
    """
    Return camera parameters.
    Later this will accept per-request overrides from the
    request body — altitude, FOV, drone GPS position.
    For now it returns the test defaults.
    """
    return TEST_PARAMS