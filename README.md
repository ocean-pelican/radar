# Radar -- Project Context for Claude Code

This file is read automatically by Claude Code at the start of every session.
It contains everything needed to pick up where we left off without re-explaining the project.

---

## What this project is

Radar is a miniature aerial object detection and geolocation pipeline.
It takes drone imagery, runs a fine-tuned YOLOv8 model to detect objects,
converts pixel-space bounding boxes to WGS84 lat/lon coordinates using camera
telemetry, and renders results as live map pins in a React/Leaflet.js frontend.
All inference is handled asynchronously via a Redis/RQ job queue.

Built as a portfolio project modeled on the architecture of production drone
perception systems.

---

## Stack

| Layer | Technology |
|---|---|
| Detection model | YOLOv8 (Ultralytics), fine-tuned on VisDrone |
| Geolocation | Custom converter (altitude, FOV, heading rotation, cos(lat) correction) |
| Backend | FastAPI + Uvicorn |
| Job queue | Redis + RQ |
| Frontend | React + Leaflet.js |
| Hardware | Apple M1, CPU training |
| Python | 3.11, venv at .venv/ |

---

## Project structure

```
radar/
├── src/
│   ├── geolocation/
│   │   ├── __init__.py           # currently empty
│   │   ├── converter.py          # pixel_to_latlon, geolocate_detection, CameraParams, GeoDetection
│   │   ├── defaults.py
│   │   └── export.py
│   ├── detection/
│   │   ├── inference.py          # YOLOv8 inference wrapper
│   │   └── tasks.py              # RQ job definitions
│   └── api/
│       ├── main.py               # FastAPI app entrypoint
│       ├── routes.py
│       ├── models.py             # Pydantic models
│       └── dependencies.py
├── data/
│   └── VisDrone/                 # not in repo, images/ and labels/
├── runs/
│   └── detect/train/weights/
│       └── best.pt               # fine-tuned weights, not committed
├── frontend/                     # React app
├── requirements.txt
└── CLAUDE.md                     # this file
```

---

## Completed phases

All eight phases are complete.

| Phase | What was built |
|---|---|
| 1 | Environment setup, venv, Git init |
| 2 | VisDrone dataset download, annotation conversion to YOLO format |
| 3 | Pretrained YOLOv8 inference baseline |
| 4 | Fine-tuning on VisDrone subset (CPU, M1) |
| 5 | Geolocation layer: pixel coords to WGS84 lat/lon |
| 6 | FastAPI backend with RQ job queue integration |
| 7 | React + Leaflet.js frontend map UI |
| 8 | Redis/RQ async worker |

---

## Key gotchas -- read before touching anything

**Venv activation**
Always activate before running any Python: `source .venv/bin/activate`
Every new terminal tab needs this. Check with `which python3`.

**Ultralytics writes weights to a non-obvious path**
Weights always land at `runs/detect/train/weights/best.pt` regardless of run name.
Do not look for them anywhere else.

**Run uvicorn from the project root**
Running from inside `src/` causes `ModuleNotFoundError` for the `src` module.
Always: `uvicorn src.api.main:app --reload --port 8000` from `radar/`.

**Port 8000 conflicts**
If the port is in use: `lsof -i :8000` then `kill -9 <PID>`.

**RQ keyword argument**
Use `log_job_description` not `log_job_execution` in worker.py. Newer RQ versions
renamed this argument.

**src/geolocation/__init__.py is empty**
Import directly from the module file:
`from src.geolocation.converter import pixel_to_latlon, CameraParams`

---

## Key functions and signatures

### pixel_to_latlon
```python
from src.geolocation.converter import pixel_to_latlon, CameraParams

params = CameraParams(
    altitude_m=100,
    fov_horizontal_deg=60,
    fov_vertical_deg=40,
    drone_lat=40.6892,
    drone_lon=-74.0445,
    heading_deg=0.0
)

lat, lon = pixel_to_latlon(px, py, img_w, img_h, params)
# returns (float, float) rounded to 7 decimal places
```

### geolocate_detection
```python
from src.geolocation.converter import geolocate_detection

detection = {
    "class_name": "person",
    "confidence": 0.87,
    "bbox_pixels": [x1, y1, x2, y2]
}

result = geolocate_detection(detection, img_w, img_h, params)
# returns GeoDetection dataclass with:
#   center_lat, center_lon
#   bbox_lat_lon (dict with top_left, top_right, bottom_left, bottom_right)
#   class_name, confidence, altitude_m, geolocation_method
```

### geolocate_all
```python
from src.geolocation.converter import geolocate_all

results = geolocate_all(detections_list, img_w, img_h, params)
# returns list of GeoDetection objects
```

---

## Running the full stack

Four processes, four terminal tabs, all from project root:

```bash
# Tab 1
redis-server

# Tab 2
source .venv/bin/activate && python3 src/worker.py

# Tab 3
source .venv/bin/activate && uvicorn src.api.main:app --reload --port 8000

# Tab 4
cd frontend && npm start
```

API docs: http://localhost:8000/docs
Frontend: http://localhost:3000

---

## Geolocation math summary

1. Ground footprint from altitude and FOV:
   `ground_width = 2 * altitude * tan(fov_h / 2)`

2. Pixel offset from image center converted to meters.
   Y axis is flipped (pixels go down, latitude goes up).

3. Heading rotation applied via 2D rotation matrix if drone is not facing north.

4. Meters converted to degrees:
   `lat = drone_lat + (y_meters / 111320)`
   `lon = drone_lon + (x_meters / (111320 * cos(drone_lat)))`
   The cos(lat) correction accounts for longitude degrees shrinking away from equator.

---

## Current state and open items

The pipeline is complete and verified end-to-end. Phase 5 (geolocation) has been
unit tested and confirmed correct.

Possible next extensions:
- Docker containerization for clean demo deployment
- Multi-class confidence filtering in the frontend UI
- Recorded walkthrough video for portfolio
- CLAUDE.md is now the source of truth for project context across sessions