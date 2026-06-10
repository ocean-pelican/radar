import json
from pathlib import Path
from datetime import datetime


def detections_to_geojson(geo_detections: list, metadata: dict = None) -> dict:
    """
    Convert a list of geo detection dicts to a GeoJSON FeatureCollection.
    This is the format Leaflet.js expects.
    """
    features = []

    for det in geo_detections:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [det["center_lon"], det["center_lat"]]  # GeoJSON is lon, lat
            },
            "properties": {
                "class_name": det["class_name"],
                "confidence": det["confidence"],
                "bbox_pixels": det["bbox_pixels"],
                "altitude_m": det["altitude_m"],
                "geolocation_method": det["geolocation_method"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "metadata": metadata or {},
        "features": features
    }

    return geojson


def save_geojson(geojson: dict, output_path: str):
    """Save a GeoJSON dict to a file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"GeoJSON saved: {output_path}")