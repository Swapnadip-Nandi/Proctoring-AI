# 🎯 Integrated Proctoring Dashboard - User Guide

## 🌟 **What is it?**

The **Integrated Proctoring Dashboard** combines ALL proctoring AI modules into a single, unified interface with real-time monitoring and alerts.

## ✨ **Features**

### **All-in-One Detection:**
- 👁️ **Eye Gaze Tracking** - Detects looking left, right, up, or center
- 🎯 **Head Pose Detection** - Monitors head orientation (up/down/left/right/straight)
- 👤 **Person Count** - Counts number of people in frame
- 📱 **Phone Detection** - Alerts when mobile phone is detected
- 🎭 **Face Detection** - Tracks facial landmarks in real-time

### **Smart Alert System:**
- 🟢 **NORMAL** - All checks passed
- 🟡 **WARNING** - Minor violations detected
- 🔴 **ALERT** - Serious violations (multiple people, phone detected, etc.)

### **Real-Time Dashboard:**
- Live status for all detection modules
- Visual alert indicators
- Timestamp tracking
- Screenshot capability
- Performance monitoring (FPS)

---

## 🚀 **How to Run**

### **Option 1: Using PowerShell Script (Easiest)**
```powershell
.\START.ps1
# Then select option 1
```

### **Option 2: Using run_demo.py**
```powershell
python run_demo.py dashboard
```

### **Option 3: Direct Launch**
```powershell
python integrated_dashboard.py
```

---

## 🎮 **Controls**

| Key | Action |
|-----|--------|
| **'q'** | Quit the dashboard |
| **'s'** | Save screenshot with timestamp |

---

## 📊 **Dashboard Layout**

```
┌─────────────────────────────────────────────────────────────┐
│ PROCTORING AI DASHBOARD          [Timestamp]    [ALERT LEVEL]│
│────────────────────────────────────────────────────────────│
│ Face: ✓ Detected                                            │
│ Eyes: Center ●                                              │
│ Head: Head Straight ●                                       │
│ Count: 1 Person ✓                                           │
│ Phone: No Phone ✓                                           │
│────────────────────────────────────────────────────────────│
│                                                              │
│           [Live Camera Feed with Overlays]                   │
│     [Face rectangles, landmark points, direction lines]      │
│                                                              │
│────────────────────────────────────────────────────────────│
│ ⚠ ALERTS: [Active alerts shown here if any]                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 **Alert Conditions**

### **ALERT Level** (Red):
- No person detected
- More than one person detected
- Mobile phone detected
- Multiple violations simultaneously

### **WARNING Level** (Orange):
- Eye movement (looking away from center)
- Head movement (not straight)
- Single minor violation

### **NORMAL Level** (Green):
- Face detected ✓
- Eyes looking at center ✓
- Head position straight ✓
- Exactly 1 person ✓
- No phone detected ✓

---

## 💡 **Pro Tips**

1. **Lighting**: Ensure good lighting for better face detection
2. **Position**: Sit directly facing the camera
3. **Distance**: Stay 2-3 feet from camera for optimal detection
4. **Background**: Avoid busy backgrounds for better person detection
5. **Screenshots**: Press 's' to capture evidence of violations

---

## 📸 **Screenshot Feature**

Screenshots are automatically saved with timestamps:
- Format: `proctoring_screenshot_YYYYMMDD_HHMMSS.jpg`
- Location: Same directory as the script
- Includes: All overlays and detection status

---

## ⚡ **Performance**

- **Face Detection**: ~7-8 FPS
- **Eye Tracking**: Real-time
- **Head Pose**: Real-time
- **Object Detection**: Updated every 5 frames (for performance)
- **Overall**: Smooth monitoring experience

---

## 🔧 **Troubleshooting**

### Camera not opening?
```powershell
python test_camera.py
```

### Low FPS?
- Close other camera applications
- Reduce screen resolution
- Ensure good lighting

### False alerts?
- Adjust distance from camera
- Improve lighting conditions
- Minimize background movement

---

## 🎯 **Use Cases**

### **1. Online Exams**
- Monitor student during examination
- Detect cheating attempts
- Record violations with screenshots

### **2. Remote Proctoring**
- Real-time monitoring dashboard
- Automated alert generation
- Evidence collection

### **3. Training & Testing**
- Test proctoring system capabilities
- Demonstrate AI detection features
- Evaluate system performance

---

## 📝 **What Gets Detected?**

| Feature | Detection | Alert Trigger |
|---------|-----------|---------------|
| **Face** | Presence & landmarks | No face detected |
| **Eyes** | Gaze direction | Looking away |
| **Head** | 3D orientation | Not facing forward |
| **Person** | Count in frame | ≠ 1 person |
| **Phone** | Mobile device | Any phone detected |

---

## ✅ **Advantages Over Individual Modules**

1. **Single Interface** - All features in one window
2. **Unified Alerts** - Combined alert system
3. **Better Performance** - Shared model loading
4. **Comprehensive View** - See all detections simultaneously
5. **Easy Monitoring** - Dashboard-style layout
6. **Professional** - Production-ready interface

---

## 🎓 **Next Steps**

1. **Run the dashboard**: `python run_demo.py dashboard`
2. **Test all features**: Move your eyes, head, show phone
3. **Take screenshots**: Press 's' to save evidence
4. **Review alerts**: Check real-time alert system
5. **Integrate**: Use in your proctoring system

---

## 🆚 **vs Individual Modules**

| Aspect | Individual Modules | Integrated Dashboard |
|--------|-------------------|---------------------|
| Windows | 5+ separate windows | 1 unified window |
| Setup | Run each separately | Run once |
| Monitoring | Switch between windows | Everything visible |
| Performance | 5x model loading | 1x model loading |
| User Experience | Complex | Simple & professional |
| Alerts | Separate outputs | Unified alert system |

---

## 🌟 **Recommended!**

The Integrated Dashboard is the **BEST WAY** to use the Proctoring AI system:
- ✅ Professional appearance
- ✅ Easy to use
- ✅ Complete monitoring
- ✅ Production-ready
- ✅ Performance optimized

---

**Start monitoring now:**
```powershell
python run_demo.py dashboard
```

🎯 **Press 'q' to quit | Press 's' to screenshot** 🎯
