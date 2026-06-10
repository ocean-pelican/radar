import sys
import shutil
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# How many images to use per split
TRAIN_SIZE = 1000
VAL_SIZE = 200

PROCESSED = Path("data/processed/VisDrone2019-DET")
SUBSET = Path("data/processed/VisDrone2019-DET-subset")

def copy_subset(split_name, size):
    in_img = PROCESSED / split_name / "images"
    in_lbl = PROCESSED / split_name / "labels"
    out_img = SUBSET / split_name / "images"
    out_lbl = SUBSET / split_name / "labels"

    out_img.mkdir(parents=True, exist_ok=True)
    out_lbl.mkdir(parents=True, exist_ok=True)

    images = list(in_img.glob("*.jpg"))
    sample = random.sample(images, min(size, len(images)))

    for img_path in sample:
        shutil.copy(img_path, out_img / img_path.name)
        lbl_path = in_lbl / (img_path.stem + ".txt")
        if lbl_path.exists():
            shutil.copy(lbl_path, out_lbl / lbl_path.name)

    print(f"Copied {len(sample)} images to {split_name} subset")

copy_subset("VisDrone2019-DET-train", TRAIN_SIZE)
copy_subset("VisDrone2019-DET-val", VAL_SIZE)
print("Subset created at data/processed/VisDrone2019-DET-subset")