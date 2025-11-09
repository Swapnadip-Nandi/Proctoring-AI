# Proctoring AI - Quick Start Guide

## 📋 Code Analysis Summary

### ✅ **Working Modules**
1. **Face Detection** (`face_detector.py`) - OpenCV DNN-based face detection
2. **Facial Landmarks** (`face_landmarks.py`) - TensorFlow-based landmark detection
3. **Eye Tracking** (`eye_tracker.py`) - Real-time eye gaze direction tracking
4. **Head Pose Estimation** (`head_pose_estimation.py`) - 3D head orientation detection
5. **Mouth Opening Detection** (`mouth_opening_detector.py`) - Detects mouth opening
6. **Person & Phone Detection** (`person_and_phone.py`) - YOLOv3-based object detection
7. **Face Spoofing** (`face_spoofing.py`) - Anti-spoofing detection

### 🔧 **Issues Fixed**
1. ✅ Fixed deprecated `sklearn.externals.joblib` → `joblib`
2. ✅ Added automatic YOLOv3 weights download
3. ✅ Fixed video path handling (now supports webcam with `video_path=0`)
4. ✅ Enhanced FastAPI main application with multiple endpoints
5. ✅ Created standalone demo runner for easy testing

### 📦 **Required Dependencies**
All dependencies are in `requirements.txt`:
- Python 3.13.5 (currently configured)
- TensorFlow 2.20.0 ✅ Installed
- OpenCV 4.12.0 ✅ Installed
- FastAPI, Uvicorn ✅ Installed
- NumPy, SciPy, Scikit-learn ✅ Installed

---

## 🚀 **How to Run the Application**

### **Option 1: Run Individual Modules (Recommended for Testing)**

Use the standalone demo script:

```powershell
# Show menu
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py

# Run specific modules
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py eye_tracking
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py head_pose
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py mouth_opening
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py person_phone
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py face_spoofing
```

### **Option 2: Run FastAPI Server**

Start the REST API server:

```powershell
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" main.py
```

Then access:
- API Documentation: http://localhost:8000/docs
- Available endpoints:
  - `POST /analyze_video` - Run all modules
  - `POST /eye_tracking` - Eye tracking only
  - `POST /head_pose` - Head pose only
  - `POST /mouth_detection` - Mouth detection only
  - `POST /person_phone` - Person/phone detection only

### **Option 3: Run Modules Directly**

```powershell
# Eye Tracking
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" -c "from eye_tracker import track_eye; track_eye(0)"

# Head Pose
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" -c "from head_pose_estimation import detect_head_pose; detect_head_pose(0)"

# Face Spoofing
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" face_spoofing.py
```

---

## ⚙️ **Module Details**

### **1. Eye Tracking** 👁️
- Tracks left/right eye movements
- Detects looking left, right, or up
- Press 'q' to quit

### **2. Head Pose Estimation** 🎯
- Detects head orientation (up/down/left/right)
- Uses 6-point facial landmark model
- Shows angles and direction

### **3. Mouth Opening Detection** 👄
- Press 'r' to record baseline mouth position
- Detects when mouth opens beyond threshold
- Useful for detecting speaking

### **4. Person & Phone Detection** 📱
- YOLOv3-based object detection
- Counts persons in frame
- Detects mobile phones
- **First run**: Downloads YOLOv3 weights (~240MB)

### **5. Face Spoofing Detection** 🎭
- Detects photo/video spoofing attempts
- Uses color histogram analysis
- Shows "True" (real face) or "False" (spoofed)

---

## 📊 **Performance (FPS on Intel i5)**
| Module | FPS |
|--------|-----|
| Eye Tracking | 7.1 |
| Mouth Detection | 7.2 |
| Person & Phone | 1.3 |
| Head Pose | 8.5 |
| Face Spoofing | 6.9 |

---

## 🐛 **Known Limitations**

1. **Audio Module** - Not included in quick start (requires pyaudio, speech_recognition)
2. **YOLOv3 Download** - First run of person_phone module downloads 240MB file
3. **Webcam Required** - Most modules require webcam access
4. **TensorFlow Import Warnings** - Linter shows false positives, code works fine

---

## 🔍 **Troubleshooting**

### Camera Not Found
```python
# Edit the module file and change video source:
video_path = 1  # Try different camera index (0, 1, 2, etc.)
```

### Module Errors
```powershell
# Check Python environment
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" -c "import cv2, tensorflow; print('OK')"
```

### YOLOv3 Download Issues
```powershell
# Manual download:
wget https://pjreddie.com/media/files/yolov3.weights -OutFile "d:\Computer Vision\Draft2\Proctoring-AI\models\yolov3.weights"
```

---

## 📝 **Example Usage**

### Quick Test - Eye Tracking
```powershell
cd "d:\Computer Vision\Draft2\Proctoring-AI"
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" run_demo.py eye_tracking
```

### Run API Server
```powershell
cd "d:\Computer Vision\Draft2\Proctoring-AI"
"D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe" main.py
```

Then test with curl:
```powershell
curl -X POST http://localhost:8000/eye_tracking
```

---

## ✅ **All Fixed & Ready to Run!**

The application is now properly configured and ready to use. Start with individual modules using `run_demo.py` to test each feature.
