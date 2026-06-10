from src.geolocation.converter import CameraParams

# VisDrone dataset typical altitude range is 5–140m
# Most sequences are in the 40–80m range
# FOV is typical for a DJI Phantom/Inspire class drone

VISDRONE_DEFAULT = CameraParams(
    altitude_m=80.0,
    fov_horizontal_deg=84.0,
    fov_vertical_deg=54.0,
    drone_lat=39.9042,      # placeholder — Beijing area where VisDrone was collected
    drone_lon=116.4074,
    heading_deg=0.0
)

# For testing with a US location (McKinney TX)
TEST_PARAMS = CameraParams(
    altitude_m=80.0,
    fov_horizontal_deg=84.0,
    fov_vertical_deg=54.0,
    drone_lat=33.1972,
    drone_lon=-96.6397,
    heading_deg=0.0
)