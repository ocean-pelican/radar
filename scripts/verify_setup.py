import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import FastAPI

print("ultralytics:", __import__('ultralytics').__version__)
print("opencv:", cv2.__version__)
print("numpy:", np.__version__)
print("All imports OK — environment is healthy")