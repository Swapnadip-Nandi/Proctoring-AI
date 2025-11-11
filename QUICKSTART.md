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







# 🚀 QUICK START GUIDE

## ✅ Everything is Ready!

All features have been implemented and tested successfully.

---

## 🎯 What's New:

### 1. **Capture Phase Removed** ✓
- Normal screenshot prevention (not ultra-aggressive)
- Right-click only blocked during monitoring

### 2. **Hindi Audio Detection** ✓
- Speaks in Hindi? ✓ Detected!
- Speaks in English? ✓ Detected!
- Auto-detects language
- Hindi suspicious keywords: jawab, uttar, madad, kya, kaise, batao, bata

### 3. **Monitoring Logs Page** ✓
- **NEW PAGE:** http://localhost:5000/monitoring_logs
- View all CRITICAL violations with screenshots
- Click images to zoom
- Filter by severity
- Download PDF report

---

## 🚀 Start the System:

```powershell
cd "d:\Computer Vision\Draft2\Proctoring-AI"
python flask_app.py
```

**URLs:**
- **Dashboard:** http://localhost:5000
- **Monitoring Logs:** http://localhost:5000/monitoring_logs

---

## 🧪 Test Features:

### Test 1: Hindi Audio Detection
1. Click "Start Monitoring"
2. Speak in Hindi: **"मुझे मदद चाहिए"** (I need help)
3. **Expected:**
   - Volume bar moves
   - "Speech detected (Hindi)" in console
   - Suspicious keyword "madad" detected

### Test 2: Trigger Violations (to populate Monitoring Logs)
1. **NO_PERSON:** Cover camera with hand for 3 seconds
2. **PHONE:** Hold phone near camera
3. **MULTIPLE_PEOPLE:** Have someone sit next to you

### Test 3: View Monitoring Logs
1. Click **"Monitoring Logs"** button in navbar
2. See violation cards with screenshots
3. Click image to zoom
4. Try filter buttons
5. Click **"Download PDF"** to get report

---

## 📸 What You'll See in Monitoring Logs:

```
┌─────────────────────────────────────────┐
│ [<- Back]         [Download PDF]        │
├─────────────────────────────────────────┤
│ Total: 5 | Critical: 3 | Warnings: 2   │
├─────────────────────────────────────────┤
│ [All] [Critical Only] [Warnings Only]   │
├─────────────────────────────────────────┤
│ ┌──────┐  PHONE DETECTED               │
│ │IMAGE │  Time: 2025-11-11 15:03:05    │
│ │ 📱   │  Severity: CRITICAL            │
│ └──────┘  Description: Mobile phone...  │
├─────────────────────────────────────────┤
│ ┌──────┐  NO PERSON                    │
│ │IMAGE │  Time: 2025-11-11 15:05:12    │
│ │ ❌   │  Severity: CRITICAL            │
│ └──────┘  Description: No person in...  │
└─────────────────────────────────────────┘
```

---

## 📁 Files Created:

```
violations.db                  ← Database (auto-created)
static/violations/             ← Screenshots folder (auto-created)
  ├── violation_20251111_150305_123456.jpg
  ├── violation_20251111_150512_789012.jpg
  └── ...
```

---

## 📦 Optional: Install ReportLab (for PDF)

Already installed! ✓

If you need to reinstall:
```powershell
pip install reportlab
```

---

## 🎨 Monitoring Logs Features:

### ✅ Implemented:
- [x] One image per violation
- [x] All CRITICAL violations displayed
- [x] Viewable on screen
- [x] Screenshot/frame captured automatically
- [x] Timestamp shown
- [x] Violation type displayed
- [x] Severity badges (CRITICAL/WARNING/INFO)
- [x] Description of why alert triggered
- [x] Click image to zoom (fullscreen modal)
- [x] Statistics dashboard
- [x] Filter buttons
- [x] PDF report download
- [x] Navigation link in dashboard

---

## 🗣️ Hindi Audio Examples:

| Hindi Text | English | Detection |
|------------|---------|-----------|
| मुझे मदद चाहिए | I need help | ✓ madad (suspicious) |
| जवाब क्या है | What is the answer | ✓ jawab (suspicious) |
| बताओ | Tell me | ✓ batao (suspicious) |
| कैसे करूं | How to do | ✓ kaise (suspicious) |
| उत्तर | Answer | ✓ uttar (suspicious) |

---

## ⚡ Quick Commands:

### Start system:
```powershell
python flask_app.py
```

### Test database:
```powershell
python violations_db.py
```

### Run verification:
```powershell
python test_final_implementation.py
```

### Check violations:
```python
from violations_db import get_violations_db
db = get_violations_db()
violations = db.get_all_violations()
print(f"Total: {len(violations)}")
```

---

## 🎯 URLs:

- **Main Dashboard:** http://localhost:5000
- **Monitoring Logs:** http://localhost:5000/monitoring_logs
- **API - Get Violations:** http://localhost:5000/api/get_violations
- **API - Get Status:** http://localhost:5000/api/status

---

## 📊 What Gets Logged to Monitoring Logs:

### CRITICAL Violations (with screenshots):
- ❌ NO_PERSON - No person detected for 3+ seconds
- 👥 MULTIPLE_PEOPLE - Multiple people in frame
- 📱 PHONE_DETECTED - Mobile phone detected
- 🗣️ SUSPICIOUS_AUDIO - Suspicious conversation/keywords
- 🖼️ SCREENSHOT_ATTEMPT - Screenshot attempt detected
- 🔧 DEVTOOLS_DETECTED - Browser dev tools opened
- 🪟 TAB_SWITCH - User switched tabs/minimized

### WARNING Violations (logged but no screenshot):
- 👀 EYE_MOVEMENT - Looking left/right
- 👇 HEAD_DOWN - Head looking down
- 👆 HEAD_UP - Head looking up
- 🎤 SPEECH_DETECTED - Normal speech detected

---

## 🔍 Database Schema:

```sql
violations table:
├── id (INTEGER PRIMARY KEY)
├── timestamp (TEXT) ← "2025-11-11 15:03:05"
├── violation_type (TEXT) ← "PHONE_DETECTED"
├── severity (TEXT) ← "CRITICAL"
├── description (TEXT) ← "Mobile phone detected..."
├── image_path (TEXT) ← "static/violations/violation_xxx.jpg"
├── metadata (JSON) ← {alert_level, session_id}
└── created_at (TIMESTAMP) ← Auto-generated
```

---

## 🎉 Success Checklist:

After starting Flask app, verify:

- [ ] Flask starts without errors
- [ ] Dashboard loads at http://localhost:5000
- [ ] "Monitoring Logs" button visible in navbar
- [ ] Can click "Start Monitoring"
- [ ] Camera shows video feed
- [ ] Audio detection card shows volume
- [ ] Speak in Hindi → Volume bar moves
- [ ] Trigger violation → Logged in Activity Log
- [ ] Click "Monitoring Logs" → New page opens
- [ ] Violation cards show screenshots
- [ ] Click image → Zooms to fullscreen
- [ ] Filter buttons work
- [ ] Statistics show correct numbers
- [ ] "Download PDF" → PDF file downloads

---

## 🆘 Troubleshooting:

### Issue: "No violations showing"
**Solution:** Trigger some violations first (cover camera, hold phone)

### Issue: "Images not loading"
**Solution:** Check `static/violations/` folder exists and contains .jpg files

### Issue: "PDF download fails"
**Solution:** Check reportlab installed: `pip install reportlab`

### Issue: "Hindi not detected"
**Solution:** 
- Check internet connection (Google Speech API)
- Speak clearly and loudly
- Check microphone permissions

### Issue: "Volume always 0%"
**Solution:**
- Check microphone permissions in Windows
- Verify microphone is set as default device
- Restart Flask app

---

## 📚 Documentation:

- **Complete Guide:** `COMPLETE_IMPLEMENTATION.md`
- **Testing Guide:** `test_final_implementation.py`
- **Database Docs:** `violations_db.py`

---

## 🎯 READY TO USE!

Everything is set up and tested. Start the Flask app and begin testing! 🚀

```powershell
python flask_app.py
```

**Then visit:** http://localhost:5000

**Happy Proctoring!** 🎓
