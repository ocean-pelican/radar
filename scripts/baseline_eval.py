import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO

model = YOLO("models/pretrained/yolov8n.pt")

metrics = model.val(
    data="data/visdrone.yaml",
    split="val",
    verbose=False
)

print("\n--- Baseline Metrics (pretrained COCO weights on VisDrone) ---")
print(f"mAP50:     {metrics.box.map50:.4f}")
print(f"mAP50-95:  {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall:    {metrics.box.mr:.4f}")