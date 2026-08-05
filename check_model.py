# pyrefly: ignore [missing-import]
from ultralytics import YOLO
import torch

print("torch:", torch.__version__)
model = YOLO("yolov8m-seg.pt")
print("Model loaded successfully")
print("Classes:", model.names)
print("Type:", type(model.names))
print("Number of classes:", len(model.names))
