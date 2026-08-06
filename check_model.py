# pyrefly: ignore [missing-import]
from ultralytics import YOLO
import torch
import os

print("torch:", torch.__version__)

# Check both YOLOv8 and YOLO 11 model files
for model_path in ["yolov8m-seg.pt", "yolo11m-seg.pt"]:
    if os.path.isfile(model_path):
        print(f"\n--- {model_path} ---")
        model = YOLO(model_path)
        print("Model loaded successfully")
        print("Classes:", model.names)
        print("Type:", type(model.names))
        print("Number of classes:", len(model.names))
    else:
        print(f"\n--- {model_path} ---")
        print(f"Model file not found: {model_path}")