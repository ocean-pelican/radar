import os
from pathlib import Path

# Paths
RAW_ROOT = Path("data/raw/VisDrone2019-DET")
OUT_ROOT = Path("data/processed/VisDrone2019-DET")

# VisDrone splits to process
SPLITS = [
    "VisDrone2019-DET-train",
    "VisDrone2019-DET-val",
    "VisDrone2019-DET-test-dev",
]

# Classes to keep (ignore class 0 and 11)
KEEP_CLASSES = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

# Remap to 0-indexed for YOLO
CLASS_REMAP = {c: i for i, c in enumerate(sorted(KEEP_CLASSES))}


def convert_annotation(ann_path, img_w, img_h):
    yolo_lines = []
    with open(ann_path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 6:
                continue

            x, y, w, h = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            score = int(parts[4])
            class_id = int(parts[5])

            # Skip ignored regions and invalid annotations
            if score == 0 or class_id not in KEEP_CLASSES:
                continue

            # Skip degenerate boxes
            if w <= 0 or h <= 0:
                continue

            # Convert to YOLO normalized center format
            x_center = (x + w / 2) / img_w
            y_center = (y + h / 2) / img_h
            w_norm = w / img_w
            h_norm = h / img_h

            remapped_id = CLASS_REMAP[class_id]
            yolo_lines.append(f"{remapped_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

    return yolo_lines


def process_split(split_name):
    in_img_dir = RAW_ROOT / split_name / "images"
    in_ann_dir = RAW_ROOT / split_name / "annotations"

    out_img_dir = OUT_ROOT / split_name / "images"
    out_lbl_dir = OUT_ROOT / split_name / "labels"

    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_lbl_dir.mkdir(parents=True, exist_ok=True)

    images = list(in_img_dir.glob("*.jpg"))
    print(f"Processing {split_name}: {len(images)} images")

    for img_path in images:
        ann_path = in_ann_dir / (img_path.stem + ".txt")

        # Symlink image (saves disk space vs copying)
        out_img = out_img_dir / img_path.name
        if not out_img.exists():
            os.symlink(img_path.resolve(), out_img)

        # Skip if no annotation file (test set)
        if not ann_path.exists():
            continue

        # Get image dimensions
        import cv2
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        img_h, img_w = img.shape[:2]

        # Convert and write labels
        yolo_lines = convert_annotation(ann_path, img_w, img_h)
        out_lbl = out_lbl_dir / (img_path.stem + ".txt")
        with open(out_lbl, "w") as f:
            f.write("\n".join(yolo_lines))

    print(f"Done: {split_name}")


if __name__ == "__main__":
    for split in SPLITS:
        process_split(split)
    print("Conversion complete. Data ready at data/processed/")