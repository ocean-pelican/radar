import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class CameraParams:
    """
    Physical parameters of the camera and drone.
    These come from drone specs or are assumed for testing.
    """
    altitude_m: float           # height above ground in meters
    fov_horizontal_deg: float   # horizontal field of view in degrees
    fov_vertical_deg: float     # vertical field of view in degrees
    drone_lat: float            # drone GPS latitude
    drone_lon: float            # drone GPS longitude
    heading_deg: float = 0.0    # drone heading (0 = north, 90 = east)


@dataclass
class GeoDetection:
    """
    A single detection enriched with geolocation data.
    """
    class_name: str
    confidence: float
    bbox_pixels: list           # [x1, y1, x2, y2]
    center_lat: float           # geolocation of box center
    center_lon: float
    bbox_lat_lon: dict          # corners of the box in lat/lon
    altitude_m: float
    geolocation_method: str     # how the fix was derived


def pixel_to_latlon(
    px: float,
    py: float,
    img_w: int,
    img_h: int,
    params: CameraParams
) -> tuple[float, float]:
    """
    Convert a pixel coordinate to a lat/lon coordinate.

    px, py      — pixel position in the image
    img_w/h     — image dimensions in pixels
    params      — camera and drone parameters

    Returns (latitude, longitude)
    """
    # Ground footprint in meters
    ground_width = 2 * params.altitude_m * math.tan(
        math.radians(params.fov_horizontal_deg / 2)
    )
    ground_height = 2 * params.altitude_m * math.tan(
        math.radians(params.fov_vertical_deg / 2)
    )

    # Pixel offset from image center
    px_offset = px - (img_w / 2)
    py_offset = (img_h / 2) - py  # flip y — pixels go down, lat goes up

    # Convert pixel offset to meters
    x_meters = (px_offset / img_w) * ground_width
    y_meters = (py_offset / img_h) * ground_height

    # Apply heading rotation if drone isn't facing north
    heading_rad = math.radians(params.heading_deg)
    x_rotated = x_meters * math.cos(heading_rad) - y_meters * math.sin(heading_rad)
    y_rotated = x_meters * math.sin(heading_rad) + y_meters * math.cos(heading_rad)

    # Convert meters to degrees
    # 111320 meters per degree of latitude (approximately constant)
    # Longitude degrees shrink as you move away from equator
    lat = params.drone_lat + (y_rotated / 111320)
    lon = params.drone_lon + (x_rotated / (111320 * math.cos(math.radians(params.drone_lat))))

    return round(lat, 7), round(lon, 7)


def geolocate_detection(
    detection: dict,
    img_w: int,
    img_h: int,
    params: CameraParams
) -> GeoDetection:
    """
    Take a single detection dict from run_inference and return
    a GeoDetection with full lat/lon data attached.
    """
    x1, y1, x2, y2 = detection["bbox_pixels"]

    # Center of the bounding box
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    center_lat, center_lon = pixel_to_latlon(cx, cy, img_w, img_h, params)

    # All four corners of the bounding box
    corners = {
        "top_left":     pixel_to_latlon(x1, y1, img_w, img_h, params),
        "top_right":    pixel_to_latlon(x2, y1, img_w, img_h, params),
        "bottom_left":  pixel_to_latlon(x1, y2, img_w, img_h, params),
        "bottom_right": pixel_to_latlon(x2, y2, img_w, img_h, params),
    }

    return GeoDetection(
        class_name=detection["class_name"],
        confidence=detection["confidence"],
        bbox_pixels=detection["bbox_pixels"],
        center_lat=center_lat,
        center_lon=center_lon,
        bbox_lat_lon=corners,
        altitude_m=params.altitude_m,
        geolocation_method="telemetry"  # using known drone GPS + altitude
    )


def geolocate_all(
    detections: list,
    img_w: int,
    img_h: int,
    params: CameraParams
) -> list[GeoDetection]:
    """
    Geolocate every detection in a list.
    Returns a list of GeoDetection objects.
    """
    return [
        geolocate_detection(d, img_w, img_h, params)
        for d in detections
    ]