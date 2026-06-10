import sys
import random
import cv2
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.detection.inference import load_model, run_inference, draw_detections, save_result

WEIGHTS = "models/finetuned/visdrone_v1/weights/best.pt"
VAL_IMAGES = Path("data/processed/VisDrone2019-DET/VisDrone2019-DET-val/images")
OUTPUT_DIR = Path("data/processed/inference_previews")
SAMPLE_SIZE = 5

def main():
    model = load_model(WEIGHTS)
    images = list(VAL_IMAGES.glob("*.jpg"))
    sample = random.sample(images, min(SAMPLE_SIZE, len(images)))

    for img_path in sample:
        print(f"\nProcessing: {img_path.name}")
        result = run_inference(model, str(img_path), conf_threshold=0.25)

        print(f"  Detections: {result['count']}")
        for det in result["detections"]:
            print(f"    {det['class_name']:20s} conf={det['confidence']}")

        annotated = draw_detections(result)
        out_path = OUTPUT_DIR / f"finetuned_{img_path.name}"
        save_result(annotated, str(out_path))

        cv2.imshow(f"Fine-tuned - {img_path.name}", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print(f"\nDone. Previews saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()