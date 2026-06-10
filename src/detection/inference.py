import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from src.detection.classes import VISDRONE_CLASSES, ACTIVE_CLASSES

# Color map for drawing boxes — one color per class
CLASS_COLORS = {
    "pedestrian":      (0, 255, 0),      # green
    "people":          (0, 200, 0),      # dark green
    "bicycle":         (255, 165, 0),    # orange
    "car":             (0, 0, 255),      # blue
    "van":             (255, 0, 0),      # red
    "truck":           (128, 0, 128),    # purple
    "tricycle":        (0, 255, 255),    # cyan
    "awning-tricycle": (255, 255, 0),    # yellow
    "bus":             (255, 20, 147),   # pink
    "motor":           (100, 100, 255),  # light blue
}

DEFAULT_COLOR = (200, 200, 200)  # gray for anything unmapped


def load_model(weights_path: str) -> YOLO:
    """Load a YOLO model from a weights file."""
    model = YOLO(weights_path)
    print(f"Model loaded: {weights_path}")
    return model


def run_inference(model: YOLO, image_path: str, conf_threshold: float = 0.25) -> dict:
    """
    Run inference on a single image.
    Returns a dict with the image and list of detections.
    """
    results = model(image_path, conf=conf_threshold, verbose=False)
    result = results[0]

    img = cv2.imread(image_path)
    detections = []

    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]

        detections.append({
            "class_id": cls_id,
            "class_name": cls_name,
            "confidence": round(conf, 3),
            "bbox_pixels": [x1, y1, x2, y2],
        })

    return {
        "image": img,
        "image_path": image_path,
        "detections": detections,
        "count": len(detections),
    }


def draw_detections(result: dict) -> np.ndarray:
    """
    Draw bounding boxes on the image from a run_inference result.
    Returns the annotated image as a numpy array.
    """
    img = result["image"].copy()

    for det in result["detections"]:
        x1, y1, x2, y2 = det["bbox_pixels"]
        cls_name = det["class_name"]
        conf = det["confidence"]

        color = CLASS_COLORS.get(cls_name, DEFAULT_COLOR)

        # Draw box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        # Draw label background
        label = f"{cls_name} {conf:.2f}"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - lh - 6), (x1 + lw, y1), color, -1)

        # Draw label text
        cv2.putText(img, label, (x1, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return img


def save_result(annotated_img: np.ndarray, output_path: str):
    """Save an annotated image to disk."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, annotated_img)
    print(f"Saved: {output_path}")

def run_inference_with_geo(
    model,
    image_path: str,
    camera_params,
    conf_threshold: float = 0.25
) -> dict:
    """
    Run inference and attach geolocation to every detection.
    Requires a CameraParams object.
    """
    from src.geolocation.converter import geolocate_all

    result = run_inference(model, image_path, conf_threshold)

    img = result["image"]
    img_h, img_w = img.shape[:2]

    geo_detections = geolocate_all(
        result["detections"],
        img_w,
        img_h,
        camera_params
    )

    result["geo_detections"] = [
        {
            "class_name": g.class_name,
            "confidence": g.confidence,
            "bbox_pixels": g.bbox_pixels,
            "center_lat": g.center_lat,
            "center_lon": g.center_lon,
            "bbox_lat_lon": g.bbox_lat_lon,
            "altitude_m": g.altitude_m,
            "geolocation_method": g.geolocation_method,
        }
        for g in geo_detections
    ]

    return result