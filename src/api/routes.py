import os
import uuid
import cv2
import aiofiles
import uuid
from src.api.queue import detection_queue, get_job_status
from src.detection.tasks import run_detection_job
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

# ── Async Detection (Queue-based) ─────────────────────────────────────────────

@router.post("/detect/async")
async def detect_async(
    file: UploadFile = File(...),
    conf_threshold: float = 0.25,
):
    """
    Submit a detection job to the queue.
    Returns a job_id immediately — caller polls /jobs/{job_id} for results.

    This is the production pattern. The synchronous /detect endpoint
    is useful for development and testing but blocks while processing.
    This endpoint returns instantly regardless of how long detection takes.
    """
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only JPG and PNG supported.")

    # Save the uploaded file to a persistent path
    # Unlike the sync endpoint, we can't clean this up immediately —
    # the worker needs to read it after this request completes
    job_id = str(uuid.uuid4())
    saved_path = UPLOAD_DIR / f"{job_id}_{file.filename}"

    async with aiofiles.open(saved_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Enqueue the job — returns immediately
    job = detection_queue.enqueue(
        run_detection_job,
        str(saved_path),
        conf_threshold,
        job_id=job_id,
        result_ttl=3600,    # keep result in Redis for 1 hour
        failure_ttl=3600
    )

    return {
        "job_id": job.id,
        "status": "queued",
        "poll_url": f"/api/v1/jobs/{job.id}"
    }


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Poll for the result of an async detection job.

    Status values:
    - queued:     job is waiting for a worker
    - processing: worker has picked it up and is running
    - complete:   result is ready
    - failed:     something went wrong, error is included
    - not_found:  job_id doesn't exist or has expired
    """
    return get_job_status(job_id)


@router.get("/jobs")
async def list_jobs():
    """
    Returns counts of jobs in each state.
    Useful for monitoring queue health during a demo.
    """
    from rq import Queue
    from src.api.queue import redis_conn

    q = Queue("detection", connection=redis_conn)

    return {
        "queued": len(q),
        "workers": len(q.workers),
        "finished_jobs": q.count
    }