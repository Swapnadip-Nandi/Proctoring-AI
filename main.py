from fastapi import FastAPI, APIRouter
from typing import Optional

from eye_tracker import track_eye
from head_pose_estimation import detect_head_pose
from mouth_opening_detector import mouth_opening_detector
from person_and_phone import detect_phone_and_person


app = FastAPI(title="Proctoring AI", 
              description="AI-based automated proctoring system",
              version="1.0.0")


@app.get("/")
def read_root():
    return {
        "message": "Proctoring AI System",
        "endpoints": {
            "/analyze_video": "POST - Analyze video with all modules",
            "/eye_tracking": "POST - Track eye movements",
            "/head_pose": "POST - Detect head pose",
            "/mouth_detection": "POST - Detect mouth opening",
            "/person_phone": "POST - Detect person count and phones"
        }
    }


@app.post("/analyze_video")
def analyze_video(video_url: Optional[str] = None):
    """
    Analyze video with all proctoring modules.
    If video_url is None, uses webcam (device 0).
    """
    try:
        track_eye(video_url)
        detect_head_pose(video_url)
        mouth_opening_detector(video_url)
        detect_phone_and_person(video_url)
        return {"message": "Success", "status": "completed"}
    except Exception as e:
        return {"message": "Error", "error": str(e)}


@app.post("/eye_tracking")
def eye_tracking(video_url: Optional[str] = None):
    """Track eye movements in video."""
    try:
        track_eye(video_url)
        return {"message": "Eye tracking completed"}
    except Exception as e:
        return {"message": "Error", "error": str(e)}


@app.post("/head_pose")
def head_pose(video_url: Optional[str] = None):
    """Detect head pose in video."""
    try:
        detect_head_pose(video_url)
        return {"message": "Head pose detection completed"}
    except Exception as e:
        return {"message": "Error", "error": str(e)}


@app.post("/mouth_detection")
def mouth_detection(video_url: Optional[str] = None):
    """Detect mouth opening in video."""
    try:
        mouth_opening_detector(video_url)
        return {"message": "Mouth detection completed"}
    except Exception as e:
        return {"message": "Error", "error": str(e)}


@app.post("/person_phone")
def person_phone(video_url: Optional[str] = None):
    """Detect persons and phones in video."""
    try:
        detect_phone_and_person(video_url)
        return {"message": "Person and phone detection completed"}
    except Exception as e:
        return {"message": "Error", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print("Starting Proctoring AI Server...")
    print("Access API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
