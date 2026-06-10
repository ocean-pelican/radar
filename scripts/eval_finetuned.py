import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO

WEIGHTS = "models/finetuned/visdrone_v1/weights/best.pt"

model = YOLO(WEIGHTS)

metrics = model.val(
    data="data/visdrone.yaml",
    split="val",
    verbose=False
)

print("\n--- Fine-tuned Model Metrics ---")
print(f"mAP50:     {metrics.box.map50:.4f}")
print(f"mAP50-95:  {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall:    {metrics.box.mr:.4f}")
print("\nPer-class AP50:")
for i, name in enumerate(model.names.values()):
    print(f"  {name:20s} {metrics.box.ap50[i]:.4f}")