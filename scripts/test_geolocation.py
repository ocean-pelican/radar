import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from src.detection.inference import load_model, run_inference
from src.geolocation.converter import geolocate_all
from src.geolocation.defaults import TEST_PARAMS

WEIGHTS = "models/finetuned/visdrone_v1/weights/best.pt"
VAL_IMAGES = Path("data/processed/VisDrone2019-DET/VisDrone2019-DET-val/images")


def main():
    model = load_model(WEIGHTS)

    # Grab one image
    images = list(VAL_IMAGES.glob("*.jpg"))
    img_path = images[0]

    img = cv2.imread(str(img_path))
    img_h, img_w = img.shape[:2]

    print(f"Image: {img_path.name}")
    print(f"Dimensions: {img_w}w x {img_h}h")
    print(f"Drone position: {TEST_PARAMS.drone_lat}, {TEST_PARAMS.drone_lon}")
    print(f"Altitude: {TEST_PARAMS.altitude_m}m")
    print()

    # Run detection
    result = run_inference(model, str(img_path), conf_threshold=0.25)
    print(f"Detections: {result['count']}")

    # Geolocate
    geo_detections = geolocate_all(
        result["detections"],
        img_w,
        img_h,
        TEST_PARAMS
    )

    # Print results
    for i, det in enumerate(geo_detections):
        print(f"\nDetection {i + 1}: {det.class_name} ({det.confidence})")
        print(f"  Pixel center:  ({(det.bbox_pixels[0] + det.bbox_pixels[2])//2}, "
              f"{(det.bbox_pixels[1] + det.bbox_pixels[3])//2})")
        print(f"  Geo center:    {det.center_lat}, {det.center_lon}")
        print(f"  Method:        {det.geolocation_method}")
        print(f"  Google Maps:   https://maps.google.com/?q={det.center_lat},{det.center_lon}")


if __name__ == "__main__":
    main()