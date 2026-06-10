import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.detection.inference import load_model, run_inference_with_geo
from src.geolocation.defaults import TEST_PARAMS
from src.geolocation.export import detections_to_geojson, save_geojson

WEIGHTS = "models/finetuned/visdrone_v1/weights/best.pt"
VAL_IMAGES = Path("data/processed/VisDrone2019-DET/VisDrone2019-DET-val/images")
OUTPUT_DIR = Path("data/processed/geojson_output")


def main():
    model = load_model(WEIGHTS)
    images = list(VAL_IMAGES.glob("*.jpg"))
    sample = random.sample(images, 5)

    all_detections = []

    for img_path in sample:
        print(f"Processing: {img_path.name}")
        result = run_inference_with_geo(model, str(img_path), TEST_PARAMS)
        print(f"  {result['count']} detections geolocated")
        all_detections.extend(result["geo_detections"])

    # Export everything as one GeoJSON file
    geojson = detections_to_geojson(
        all_detections,
        metadata={
            "image_count": len(sample),
            "total_detections": len(all_detections),
            "altitude_m": TEST_PARAMS.altitude_m,
            "drone_lat": TEST_PARAMS.drone_lat,
            "drone_lon": TEST_PARAMS.drone_lon,
        }
    )

    save_geojson(geojson, str(OUTPUT_DIR / "detections.geojson"))
    print(f"\nTotal detections exported: {len(all_detections)}")
    print(f"Open data/processed/geojson_output/detections.geojson to inspect")


if __name__ == "__main__":
    main()