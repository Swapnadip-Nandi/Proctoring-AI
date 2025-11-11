"""
Flask-based Proctoring AI Web Dashboard
Professional web interface with real-time video streaming
"""

from flask import Flask, render_template, Response, jsonify, send_file, request
import cv2
import numpy as np
import os
import sys
import json
from datetime import datetime
from threading import Lock

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import detection modules
from face_detector import get_face_detector, find_faces
from face_landmarks import get_landmark_model, detect_marks
from eye_tracker import eye_on_mask, find_eyeball_position, contouring, process_thresh

# Import violations database
from violations_db import get_violations_db

# Import YOLO with error handling (it has Lambda layer issues)
try:
    from person_and_phone import yolo
    YOLO_AVAILABLE = True
except Exception as e:
    print(f"Warning: YOLO not available: {e}")
    YOLO_AVAILABLE = False
    yolo = None

# Import audio detector
try:
    from audio_detector import get_audio_detector
    AUDIO_AVAILABLE = True
    print("✓ Audio detection module loaded")
except Exception as e:
    print(f"Warning: Audio detection not available: {e}")
    AUDIO_AVAILABLE = False

print("Loading AI models for Flask dashboard...")

# Initialize models
face_model = get_face_detector()
landmark_model = get_landmark_model()

# Initialize violations database
violations_db = get_violations_db()

# Create violations images directory
os.makedirs("static/violations", exist_ok=True)

# Initialize audio detector if available
if AUDIO_AVAILABLE:
    audio_detector = get_audio_detector()
else:
    audio_detector = None

# Eye tracking setup
left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]
kernel = np.ones((9, 9), np.uint8)

# Head pose model points
model_points = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye left corner
    (225.0, 170.0, -135.0),      # Right eye right corner
    (-150.0, -150.0, -125.0),    # Left Mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
])

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'proctoring-ai-secret-key'

# Global variables for dashboard state
class DashboardState:
    def __init__(self):
        self.lock = Lock()
        self.camera = None
        self.is_monitoring = False
        self.status = {
            'face_detected': False,
            'eye_status': 'Not Detected',
            'head_status': 'Not Detected',
            'person_count': 0,
            'phone_detected': False,
            'audio_detected': False,
            'speech_detected': False,
            'suspicious_audio': False,
            'volume_level': 0,
            'alert_level': 'NORMAL',
            'alerts': [],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_violations': 0,
            'session_start': None,
            'frames_processed': 0
        }
        self.violation_log = []
        self.activity_log = []  # New: track all activities
        self.detection_history = {  # Multi-frame validation
            'phone': [],
            'person_count': [],
            'face': []
        }
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize camera"""
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                import time
                time.sleep(0.5)
                self.is_monitoring = True
                self.status['session_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.add_activity_log("System started", "INFO")
                print("✓ Camera initialized successfully")
            else:
                print("✗ Failed to open camera")
                self.is_monitoring = False
    
    def add_activity_log(self, message, level="INFO"):
        """Add entry to activity log"""
        self.activity_log.append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'message': message,
            'level': level
        })
        # Keep only last 50 activities
        if len(self.activity_log) > 50:
            self.activity_log.pop(0)
    
    def validate_detection(self, key, value, threshold=3):
        """Multi-frame validation for stable detections"""
        history = self.detection_history[key]
        history.append(value)
        
        # Keep last 5 frames
        if len(history) > 5:
            history.pop(0)
        
        # Need at least 'threshold' frames with same value
        if len(history) >= threshold:
            return sum(history[-threshold:]) >= threshold if isinstance(value, bool) else \
                   all(v == history[-1] for v in history[-threshold:])
        return False
    
    def reset_status(self):
        """Reset detection status for new frame"""
        with self.lock:
            self.status['face_detected'] = False
            self.status['eye_status'] = 'Not Detected'
            self.status['head_status'] = 'Not Detected'
            # Don't reset person_count, phone_detected, and audio - they're validated
            self.status['alerts'] = []
    
    def update_alert_level(self, frame=None):
        """Update alert level based on detections with improved accuracy"""
        alerts = []
        
        # Face detection alert
        if not self.status['face_detected']:
            alerts.append('NO_FACE')
            self.add_activity_log("⚠️ No face detected", "WARNING")
        
        # Person count alert with multi-frame validation
        validated_person_count = self.status['person_count']
        if self.validate_detection('person_count', self.status['person_count'] == 0):
            alerts.append('NO_PERSON')
            self.add_activity_log("⚠️ No person in frame", "WARNING")
        elif self.validate_detection('person_count', self.status['person_count'] > 1):
            alerts.append('MULTIPLE_PEOPLE')
            self.add_activity_log(f"🚨 Multiple people detected ({self.status['person_count']})", "CRITICAL")
        
        # Phone detection with multi-frame validation
        if self.validate_detection('phone', self.status['phone_detected']):
            alerts.append('PHONE_DETECTED')
            self.add_activity_log("🚨 Mobile phone detected", "CRITICAL")
        
        # Audio detection alerts
        if self.status['speech_detected']:
            alerts.append('SPEECH_DETECTED')
            self.add_activity_log("⚠️ Speech detected during exam", "WARNING")
        
        if self.status['suspicious_audio']:
            alerts.append('SUSPICIOUS_AUDIO')
            self.add_activity_log("🚨 Suspicious conversation detected", "CRITICAL")
        
        # Eye movement detection
        if 'Looking Left' in self.status['eye_status'] or 'Looking Right' in self.status['eye_status']:
            alerts.append('EYE_MOVEMENT')
            self.add_activity_log(f"⚠️ Suspicious eye movement: {self.status['eye_status']}", "WARNING")
        
        # Head movement detection
        if 'Down' in self.status['head_status']:
            alerts.append('HEAD_DOWN')
            self.add_activity_log("⚠️ Head looking down", "WARNING")
        elif 'Up' in self.status['head_status']:
            alerts.append('HEAD_UP')
            self.add_activity_log("⚠️ Head looking up", "WARNING")
        
        self.status['alerts'] = alerts
        
        # Set alert level with proper prioritization
        if self.status['phone_detected'] or self.status['person_count'] > 1 or self.status['suspicious_audio']:
            self.status['alert_level'] = 'CRITICAL'
            self.log_violation(', '.join(alerts), 'CRITICAL', frame=frame)
        elif self.status['person_count'] == 0 or not self.status['face_detected'] or self.status['speech_detected']:
            self.status['alert_level'] = 'ALERT'
            self.log_violation(', '.join(alerts), 'ALERT', frame=frame)
        elif len(alerts) >= 2:
            self.status['alert_level'] = 'WARNING'
            self.log_violation(', '.join(alerts), 'WARNING', frame=frame)
        else:
            self.status['alert_level'] = 'NORMAL'
        
        self.status['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_violation(self, violation_type, severity, frame=None):
        """Log violations for reporting with proper severity and frame capture"""
        self.status['total_violations'] += 1
        violation_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': violation_type,
            'severity': severity
        }
        self.violation_log.append(violation_entry)
        
        # Keep only last 100 violations in memory
        if len(self.violation_log) > 100:
            self.violation_log.pop(0)
        
        # Save to database if CRITICAL and frame available
        if severity == 'CRITICAL' and frame is not None:
            try:
                # Create unique filename
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                image_filename = f"violation_{timestamp_str}.jpg"
                image_path = os.path.join("static", "violations", image_filename)
                
                # Save frame as image
                cv2.imwrite(image_path, frame)
                
                # Get description based on violation type
                description = self._get_violation_description(violation_type)
                
                # Save to database
                violations_db.add_violation(
                    violation_type=violation_type,
                    severity=severity,
                    description=description,
                    image_path=image_path,
                    metadata={
                        'alert_level': self.status.get('alert_level', 'UNKNOWN'),
                        'session_id': self.status.get('session_start', 'N/A')
                    }
                )
                
                print(f"✓ Saved CRITICAL violation: {violation_type} → {image_path}")
                
            except Exception as e:
                print(f"❌ Error saving violation to database: {e}")
    
    def _get_violation_description(self, violation_type):
        """Get human-readable description for violation type"""
        descriptions = {
            'NO_PERSON': 'No person detected in frame for extended period',
            'MULTIPLE_PEOPLE': 'Multiple people detected in video frame',
            'PHONE_DETECTED': 'Mobile phone detected in student\'s hands or nearby',
            'HEAD_DOWN': 'Student looking down for extended period',
            'HEAD_UP': 'Student looking up for extended period',
            'EYE_LEFT': 'Student looking left (possible cheating)',
            'EYE_RIGHT': 'Student looking right (possible cheating)',
            'SPEECH_DETECTED': 'Suspicious speech or conversation detected',
            'SUSPICIOUS_AUDIO': 'Suspicious keywords detected in audio',
            'SCREENSHOT_ATTEMPT': 'Screenshot attempt detected and blocked',
            'DEVTOOLS_DETECTED': 'Browser developer tools opened',
            'TAB_SWITCH': 'User switched browser tab or minimized window',
            'Page visibility': 'User switched tab or minimized window'
        }
        
        # Check if violation_type contains any known keywords
        for key, desc in descriptions.items():
            if key.lower() in violation_type.lower():
                return desc
        
        return violation_type  # Return original if no match found


dashboard_state = DashboardState()

def detect_eye_gaze(img, shape):
    """Detect eye gaze direction"""
    try:
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask, end_points_left = eye_on_mask(mask, left, shape)
        mask, end_points_right = eye_on_mask(mask, right, shape)
        mask = cv2.dilate(mask, kernel, 5)
        
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        
        mid = int((shape[42][0] + shape[39][0]) // 2)
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(eyes_gray, 75, 255, cv2.THRESH_BINARY)
        thresh = process_thresh(thresh)
        
        eyeball_pos_left = contouring(thresh[:, 0:mid], mid, img, end_points_left)
        eyeball_pos_right = contouring(thresh[:, mid:], mid, img, end_points_right, True)
        
        if eyeball_pos_left == eyeball_pos_right and eyeball_pos_left != 0:
            if eyeball_pos_left == 1:
                return "Looking Left"
            elif eyeball_pos_left == 2:
                return "Looking Right"
            elif eyeball_pos_left == 3:
                return "Looking Up"
        
        return "Center"
    except:
        return "Not Detected"

def detect_head_pose(img, marks, camera_matrix):
    """Detect head pose orientation"""
    try:
        image_points = np.array([
            marks[30], marks[8], marks[36],
            marks[45], marks[48], marks[54]
        ], dtype="double")
        
        dist_coeffs = np.zeros((4, 1))
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, 
            dist_coeffs, flags=cv2.SOLVEPNP_UPNP
        )
        
        nose_end_point2D, _ = cv2.projectPoints(
            np.array([(0.0, 0.0, 1000.0)]), 
            rotation_vector, translation_vector, 
            camera_matrix, dist_coeffs
        )
        
        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
        
        cv2.line(img, p1, p2, (0, 255, 255), 2)
        
        try:
            m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            ang = int(np.degrees(np.arctan(m)))
        except:
            ang = 90
        
        if ang >= 48:
            return "Head Down"
        elif ang <= -48:
            return "Head Up"
        else:
            return "Head Straight"
    except:
        return "Not Detected"

def detect_objects(img):
    """Detect persons and phones using YOLO with high accuracy"""
    if not YOLO_AVAILABLE:
        return 1, False  # Default: assume 1 person, no phone
    
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (416, 416))  # Higher resolution for better accuracy
        img_normalized = np.expand_dims(img_resized.astype(np.float32) / 255.0, 0)
        
        boxes, scores, classes, nums = yolo(img_normalized)
        
        person_count = 0
        phone_detected = False
        confidence_threshold = 0.6  # Higher threshold for better accuracy
        
        for i in range(nums[0]):
            score = float(scores[0][i])
            if score < confidence_threshold:
                continue
                
            class_id = int(classes[0][i])
            
            # COCO dataset: 0 = person
            if class_id == 0:
                person_count += 1
            
            # COCO dataset: 67 = cell phone, 73 = laptop (also monitor for cheating)
            if class_id in [67, 73]:
                phone_detected = True
        
        return person_count, phone_detected
    except Exception as e:
        print(f"YOLO detection error: {e}")
        return 1, False  # Default: assume 1 person, no phone


def generate_frames():
    """Generate video frames with detections"""
    frame_count = 0
    
    while dashboard_state.is_monitoring:
        success, frame = dashboard_state.camera.read()
        
        if not success:
            break
        
        # Reset status
        dashboard_state.reset_status()
        
        # Setup camera matrix
        h, w = frame.shape[:2]
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        # Detect faces with higher confidence
        faces = find_faces(frame, face_model)
        
        if len(faces) > 0:
            dashboard_state.status['face_detected'] = True
            dashboard_state.detection_history['face'].append(True)
            
            for face in faces:
                x, y, x1, y1 = face
                cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)
                
                marks = detect_marks(frame, landmark_model, face)
                
                # Draw landmarks (smaller for cleaner look)
                for mark in marks:
                    cv2.circle(frame, (mark[0], mark[1]), 1, (0, 255, 255), -1)
                
                # Detect eye gaze
                dashboard_state.status['eye_status'] = detect_eye_gaze(frame, marks)
                
                # Detect head pose
                dashboard_state.status['head_status'] = detect_head_pose(frame, marks, camera_matrix)
                
                # Add text overlay
                cv2.putText(frame, f"Eyes: {dashboard_state.status['eye_status']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Head: {dashboard_state.status['head_status']}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            dashboard_state.detection_history['face'].append(False)
        
        # Object detection (every 3 frames for better performance)
        if frame_count % 3 == 0:
            person_count, phone_detected = detect_objects(frame)
            dashboard_state.status['person_count'] = person_count
            dashboard_state.status['phone_detected'] = phone_detected
            
            # Add multi-frame validation
            dashboard_state.detection_history['phone'].append(phone_detected)
            dashboard_state.detection_history['person_count'].append(person_count)
            
            # Display detection results
            cv2.putText(frame, f"Persons: {person_count}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            if phone_detected:
                cv2.putText(frame, "PHONE DETECTED!", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Keep detection history limited
        for key in dashboard_state.detection_history:
            if len(dashboard_state.detection_history[key]) > 5:
                dashboard_state.detection_history[key].pop(0)
        
        # Update audio detection status (every frame)
        if AUDIO_AVAILABLE and audio_detector:
            audio_status = audio_detector.get_status()
            dashboard_state.status['audio_detected'] = audio_status['audio_detected']
            dashboard_state.status['speech_detected'] = audio_status['speech_detected']
            dashboard_state.status['volume_level'] = audio_status['volume_level']
            dashboard_state.status['suspicious_audio'] = (
                audio_status['conversation_detected'] or 
                len(audio_status['suspicious_keywords']) > 0
            )
        
        # Update alert level (pass frame for CRITICAL violations)
        dashboard_state.update_alert_level(frame=frame.copy())
        dashboard_state.status['frames_processed'] = frame_count
        
        # Draw alert level on frame
        alert_colors = {'NORMAL': (0, 255, 0), 'WARNING': (0, 165, 255), 
                       'ALERT': (0, 100, 255), 'CRITICAL': (0, 0, 255)}
        alert_color = alert_colors.get(dashboard_state.status['alert_level'], (0, 255, 0))
        cv2.putText(frame, f"Status: {dashboard_state.status['alert_level']}", 
                   (w - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, alert_color, 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        frame_count += 1

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """API endpoint to get current status"""
    with dashboard_state.lock:
        return jsonify(dashboard_state.status)

@app.route('/api/violations')
def get_violations():
    """API endpoint to get violation log"""
    return jsonify({
        'violations': dashboard_state.violation_log[-20:],  # Last 20
        'total': dashboard_state.status['total_violations']
    })

@app.route('/api/activity')
def get_activity():
    """API endpoint to get activity log"""
    return jsonify({
        'activities': dashboard_state.activity_log[-30:]  # Last 30
    })

@app.route('/api/log_event', methods=['POST'])
def log_event():
    """API endpoint to log page visibility/fullscreen events"""
    from flask import request
    data = request.get_json()
    event_type = data.get('type', 'UNKNOWN')
    
    if event_type == 'PAGE_HIDDEN':
        dashboard_state.add_activity_log("🚨 User switched tab/minimized window", "CRITICAL")
        dashboard_state.log_violation("Page visibility: Tab switched or window hidden", "CRITICAL")
    elif event_type == 'FULLSCREEN_EXIT':
        dashboard_state.add_activity_log("🚨 User exited fullscreen mode", "CRITICAL")
        dashboard_state.log_violation("Fullscreen: User exited fullscreen", "CRITICAL")
    elif event_type == 'FULLSCREEN_ENTER':
        dashboard_state.add_activity_log("✓ Fullscreen mode activated", "INFO")
    elif event_type == 'PAGE_VISIBLE':
        dashboard_state.add_activity_log("✓ User returned to exam tab", "INFO")
    elif event_type == 'SCREENSHOT_ATTEMPT':
        attempts = data.get('attempts', 1)
        dashboard_state.add_activity_log(f"🚨 Screenshot attempt detected (#{attempts})", "CRITICAL")
        dashboard_state.log_violation(f"Screenshot attempt #{attempts}", "CRITICAL")
    elif event_type == 'DEVTOOLS_DETECTED':
        dashboard_state.add_activity_log("⚠️ Developer tools detected", "WARNING")
        dashboard_state.log_violation("Developer tools opened", "WARNING")
    
    return jsonify({'status': 'logged'})

@app.route('/api/start_monitoring')
def start_monitoring():
    """Start monitoring"""
    dashboard_state.initialize_camera()
    dashboard_state.is_monitoring = True
    
    # Start audio detector if available
    if AUDIO_AVAILABLE and audio_detector:
        audio_detector.start()
        dashboard_state.add_activity_log("🎤 Audio monitoring started", "INFO")
    
    dashboard_state.add_activity_log("📹 Video monitoring started", "INFO")
    return jsonify({'status': 'started', 'monitoring': dashboard_state.is_monitoring})

@app.route('/api/stop_monitoring')
def stop_monitoring():
    """Stop monitoring"""
    dashboard_state.is_monitoring = False
    if dashboard_state.camera:
        dashboard_state.camera.release()
        dashboard_state.camera = None
    
    # Stop audio detector if available
    if AUDIO_AVAILABLE and audio_detector:
        audio_detector.stop()
        dashboard_state.add_activity_log("🎤 Audio monitoring stopped", "INFO")
    
    dashboard_state.add_activity_log("📹 Video monitoring stopped", "INFO")
    return jsonify({'status': 'stopped'})

@app.route('/monitoring_logs')
def monitoring_logs():
    """Monitoring logs page with violation history"""
    return render_template('monitoring_logs.html')

@app.route('/api/get_violations')
def api_get_violations():
    """API endpoint to get all violations from database"""
    severity_filter = request.args.get('severity', None)
    limit = request.args.get('limit', type=int, default=100)
    
    violations = violations_db.get_all_violations(severity_filter=severity_filter, limit=limit)
    statistics = violations_db.get_statistics()
    
    return jsonify({
        'violations': violations,
        'statistics': statistics,
        'total': len(violations)
    })

@app.route('/api/download_report')
def download_report():
    """Download PDF report of critical violations"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from io import BytesIO
        
        # Get critical violations
        violations = violations_db.get_critical_violations(limit=50)
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=inch/2, leftMargin=inch/2,
                              topMargin=inch, bottomMargin=inch/2)
        
        # Container for elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph("🎯 Proctoring AI - Monitoring Report", title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Statistics
        stats = violations_db.get_statistics()
        stats_data = [
            ['Total Violations', str(stats['total'])],
            ['Critical Violations', str(stats['by_severity'].get('CRITICAL', 0))],
            ['Warning Violations', str(stats['by_severity'].get('WARNING', 0))],
            ['Last 24 Hours', str(stats['last_24h'])]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Violations header
        elements.append(Paragraph("Critical Violations", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add violations with images
        for i, violation in enumerate(violations, 1):
            # Violation details
            details = f"""
            <b>#{i} - {violation['violation_type']}</b><br/>
            <b>Time:</b> {violation['timestamp']}<br/>
            <b>Severity:</b> <font color="red">{violation['severity']}</font><br/>
            <b>Description:</b> {violation['description']}<br/>
            """
            elements.append(Paragraph(details, styles['Normal']))
            
            # Add image if exists
            if violation['image_path'] and os.path.exists(violation['image_path']):
                try:
                    img = RLImage(violation['image_path'], width=4*inch, height=3*inch)
                    elements.append(img)
                except Exception as e:
                    elements.append(Paragraph(f"[Image not available: {e}]", styles['Italic']))
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Page break after every 3 violations
            if i % 3 == 0 and i < len(violations):
                elements.append(Spacer(1, inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Send file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'proctoring_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except ImportError:
        return jsonify({'error': 'ReportLab not installed. Run: pip install reportlab'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎯 PROCTORING AI - WEB DASHBOARD")
    print("="*60)
    print("\n✓ All AI models loaded successfully!")
    print("✓ Camera initialized")
    print("✓ Violations database ready")
    print("\n🌐 Starting Flask server...")
    print("\n📊 Dashboard URL: http://localhost:5000")
    print("📊 Monitoring Logs: http://localhost:5000/monitoring_logs")
    print("📱 Access from any browser on your network")
    print("\nPress CTRL+C to stop the server\n")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

