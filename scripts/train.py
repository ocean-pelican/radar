import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from ultralytics import YOLO

# Detect best available device
if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

print(f"Training on: {DEVICE}")

# Paths
PRETRAINED_WEIGHTS = "models/pretrained/yolov8n.pt"
DATA_CONFIG = "data/visdrone_subset.yaml"
OUTPUT_DIR = "models/finetuned"


def train():
    model = YOLO(PRETRAINED_WEIGHTS)

    results = model.train(
        data=DATA_CONFIG,
        epochs=50,              # start here, increase later if needed
        imgsz=640,              # input resolution
        batch=16,               # reduce to 8 if you get memory errors
        device=DEVICE,
        project=OUTPUT_DIR,
        name="visdrone_v1",
        pretrained=True,
        optimizer="AdamW",
        lr0=0.001,              # initial learning rate
        lrf=0.01,               # final learning rate fraction
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,        # ramp up lr for first 3 epochs
        patience=15,            # stop early if no improvement for 15 epochs
        save=True,
        save_period=10,         # save checkpoint every 10 epochs
        val=True,               # validate after each epoch
        plots=True,             # generate training curve plots
        verbose=True,
    )

    print(f"\nTraining complete.")
    print(f"Best weights saved to: {OUTPUT_DIR}/visdrone_v1/weights/best.pt")
    return results


if __name__ == "__main__":
    train()