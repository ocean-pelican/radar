import os
import uuid
import cv2
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.api.models import DetectionResponse, HealthResponse, Detection, BoundingBox
from src.api.dependencies import get_model, get_camera_params, DEFAULT_WEIGHTS
from src.detection.inference import run_inference_with_geo
from src.geolocation.export import detections_to_geojson

router = APIRouter()

# Temporary folder for uploaded images
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Health Check ──────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Confirms the server is running and the model is loaded.
    Your frontend can ping this on startup to confirm the
    backend is ready before sending any images.
    """
    model = get_model()
    return HealthResponse(
        status="ok",
        model_loaded=model is not None,
        model_path=DEFAULT_WEIGHTS
    )


# ── Single Image Detection ────────────────────────────────────────────────────

@router.post("/detect", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    conf_threshold: float = 0.25,
):
    """
    Accept an image file, run detection and geolocation,
    return all detections as structured JSON with GeoJSON included.

    conf_threshold — minimum confidence to include a detection (0.0–1.0)
    """

    # Validate file type
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported."
        )

    # Save uploaded file to a temp path
    temp_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    async with aiofiles.open(temp_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    try:
        model = get_model()
        camera_params = get_camera_params()

        # Run detection + geolocation
        result = run_inference_with_geo(
            model,
            str(temp_path),
            camera_params,
            conf_threshold=conf_threshold
        )

        # Build response detections
        detections = []
        for det in result["geo_detections"]:
            x1, y1, x2, y2 = det["bbox_pixels"]
            detections.append(Detection(
                class_name=det["class_name"],
                confidence=det["confidence"],
                bbox_pixels=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                center_lat=det["center_lat"],
                center_lon=det["center_lon"],
                altitude_m=det["altitude_m"],
                geolocation_method=det["geolocation_method"]
            ))

        # Build GeoJSON
        geojson = detections_to_geojson(result["geo_detections"])

        return DetectionResponse(
            image_name=file.filename,
            total_detections=len(detections),
            detections=detections,
            geojson=geojson
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Always clean up the temp file
        if temp_path.exists():
            temp_path.unlink()


# ── GeoJSON Only ──────────────────────────────────────────────────────────────

@router.post("/detect/geojson")
async def detect_geojson(
    file: UploadFile = File(...),
    conf_threshold: float = 0.25,
):
    """
    Same as /detect but returns pure GeoJSON only.
    This is what the Leaflet map will call directly in Phase 7 —
    Leaflet can consume GeoJSON natively without any transformation.
    """
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only JPG and PNG supported.")

    temp_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    async with aiofiles.open(temp_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    try:
        model = get_model()
        camera_params = get_camera_params()

        result = run_inference_with_geo(
            model,
            str(temp_path),
            camera_params,
            conf_threshold=conf_threshold
        )

        geojson = detections_to_geojson(
            result["geo_detections"],
            metadata={"image_name": file.filename}
        )

        return JSONResponse(content=geojson)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_path.exists():
            temp_path.unlink()