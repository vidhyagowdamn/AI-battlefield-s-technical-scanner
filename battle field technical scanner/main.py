from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from . import detector
from pydantic import BaseModel
import math
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrajectoryInput(BaseModel):
    target_distance: float
    velocity: float = 120.0

@app.post("/api/analyze")
async def analyze_image(scope: str = Form(...), file: UploadFile = File(...)):
    image_data = await file.read()
    predictions = detector.get_object_predictions(image_data, scope)
    return {"predictions": predictions}

@app.post("/api/trajectory")
async def get_trajectory(data: TrajectoryInput):
    g = 9.81
    v = data.velocity
    d = data.target_distance
    val = (g * d) / (v**2)
    
    if val > 1 or val < -1:
        return {"error": "Target out of range"}

    angle_rad = 0.5 * math.asin(val)
    launch_angle_deg = math.degrees(angle_rad)
    time_of_flight = (2 * v * math.sin(angle_rad)) / g

    path_points = []
    for t in np.linspace(0, time_of_flight, num=50):
        x = v * math.cos(angle_rad) * t
        y = v * math.sin(angle_rad) * t - 0.5 * g * (t**2)
        if y >= 0:
            path_points.append({"x": x, "y": y})

    return {
        "path": path_points,
        "calculated_angle": launch_angle_deg,
        "time_of_flight": time_of_flight
    }
=