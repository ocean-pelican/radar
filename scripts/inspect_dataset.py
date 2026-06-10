import cv2
import numpy as np
from pathlib import Path
import random

PROCESSED = Path("data/processed/VisDrone2019-DET/VisDrone2019-DET-val")
IMG_DIR = PROCESSED / "images"
LBL_DIR = PROCESSED / "labels"

NAMES = ["bicycle","awning-tricycle","bus","car","motor",
         "people","pedestrian","tricycle","van","truck"]

COLORS = {i: tuple(np.random.randint(50, 255, 3).tolist()) for i in range(10)}

def draw_boxes(img_path):
    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]

    lbl_path = LBL_DIR / (img_path.stem + ".txt")
    if not lbl_path.exists():
        print("No label file found")
        return

    with open(lbl_path) as f:
        for line in f:
            parts = line.strip().split()
            cls = int(parts[0])
            x_c, y_c, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

            # Convert back to pixel coords for drawing
            x1 = int((x_c - bw / 2) * w)
            y1 = int((y_c - bh / 2) * h)
            x2 = int((x_c + bw / 2) * w)
            y2 = int((y_c + bh / 2) * h)

            color = COLORS[cls]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, NAMES[cls], (x1, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    cv2.imshow("VisDrone Sample", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    images = list(IMG_DIR.glob("*.jpg"))
    sample = random.choice(images)
    print(f"Showing: {sample.name}")
    draw_boxes(sample)