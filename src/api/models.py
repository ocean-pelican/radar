from pydantic import BaseModel
from typing import List, Optional


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox_pixels: BoundingBox
    center_lat: float
    center_lon: float
    altitude_m: float
    geolocation_method: str


class DetectionResponse(BaseModel):
    image_name: str
    total_detections: int
    detections: List[Detection]
    geojson: dict


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None