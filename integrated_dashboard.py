"""
Integrated Proctoring AI Dashboard
Combines all detection modules in a single interface
"""

import cv2
import numpy as np
import os
import sys
from datetime import datetime

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import all detection modules
from face_detector import get_face_detector, find_faces
from face_landmarks import get_landmark_model, detect_marks

print("Loading AI models... This may take a moment...")

# Load all models at startup
face_model = get_face_detector()
landmark_model = get_landmark_model()

# Import YOLOv3 for person and phone detection
from person_and_phone import yolo

# Import eye tracking utilities
from eye_tracker import eye_on_mask, find_eyeball_position, contouring, process_thresh

# Eye tracking landmarks
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


class ProctoringDashboard:
    def __init__(self, video_source=0):
        self.cap = cv2.VideoCapture(video_source)
        
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        
        # Give camera time to initialize
        import time
        time.sleep(0.5)
        
        # Read first frame to get dimensions
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Could not read from camera")
        
        self.frame_height, self.frame_width = frame.shape[:2]
        
        # Setup camera matrix for head pose
        focal_length = self.frame_width
        center = (self.frame_width / 2, self.frame_height / 2)
        self.camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        # Detection status
        self.reset_status()
        
        # Load class names for YOLO
        self.class_names = [c.strip() for c in open(
            os.path.join(SCRIPT_DIR, "models/classes.TXT")
        ).readlines()]
        
        print("✓ All models loaded successfully!")
        print("✓ Camera initialized")
        print("\nStarting Integrated Proctoring Dashboard...")
        print("Press 'q' to quit, 's' to save screenshot")
    
    def reset_status(self):
        """Reset all detection statuses"""
        self.eye_status = "Normal"
        self.head_status = "Normal"
        self.person_count = 0
        self.phone_detected = False
        self.face_detected = False
        self.alert_level = "NORMAL"  # NORMAL, WARNING, ALERT
        self.alerts = []
    
    def detect_eye_gaze(self, img, shape):
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
                    return "Looking Left ⬅"
                elif eyeball_pos_left == 2:
                    return "Looking Right ➡"
                elif eyeball_pos_left == 3:
                    return "Looking Up ⬆"
            
            return "Center ●"
        except:
            return "Not Detected"
    
    def detect_head_pose(self, img, marks):
        """Detect head pose orientation"""
        try:
            image_points = np.array([
                marks[30],     # Nose tip
                marks[8],      # Chin
                marks[36],     # Left eye left corner
                marks[45],     # Right eye right corner
                marks[48],     # Left Mouth corner
                marks[54]      # Right mouth corner
            ], dtype="double")
            
            dist_coeffs = np.zeros((4, 1))
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, self.camera_matrix, 
                dist_coeffs, flags=cv2.SOLVEPNP_UPNP
            )
            
            nose_end_point2D, _ = cv2.projectPoints(
                np.array([(0.0, 0.0, 1000.0)]), 
                rotation_vector, translation_vector, 
                self.camera_matrix, dist_coeffs
            )
            
            p1 = (int(image_points[0][0]), int(image_points[0][1]))
            p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
            
            # Draw direction line
            cv2.line(img, p1, p2, (0, 255, 255), 2)
            
            try:
                m = (p2[1] - p1[1]) / (p2[0] - p1[0])
                ang = int(np.degrees(np.arctan(m)))
            except:
                ang = 90
            
            if ang >= 48:
                return "Head Down ⬇"
            elif ang <= -48:
                return "Head Up ⬆"
            else:
                return "Head Straight ●"
        except:
            return "Not Detected"
    
    def detect_objects(self, img):
        """Detect persons and phones using YOLO"""
        try:
            # Prepare image for YOLO
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, (320, 320))
            img_normalized = np.expand_dims(img_resized.astype(np.float32) / 255, 0)
            
            # Run YOLO detection
            boxes, scores, classes, nums = yolo(img_normalized)
            
            person_count = 0
            phone_detected = False
            
            for i in range(nums[0]):
                if int(classes[0][i]) == 0:  # Person class
                    person_count += 1
                if int(classes[0][i]) == 67:  # Cell phone class
                    phone_detected = True
            
            return person_count, phone_detected
        except:
            return 0, False
    
    def draw_dashboard(self, img):
        """Draw dashboard overlay with all detection results"""
        overlay = img.copy()
        h, w = img.shape[:2]
        
        # Semi-transparent background for status panel
        cv2.rectangle(overlay, (10, 10), (w - 10, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        # Title
        cv2.putText(img, "PROCTORING AI DASHBOARD", (20, 40),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(img, timestamp, (w - 250, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Detection Status
        y_offset = 75
        line_height = 30
        
        # Face Detection
        color = (0, 255, 0) if self.face_detected else (0, 0, 255)
        status = "✓ Detected" if self.face_detected else "✗ Not Found"
        cv2.putText(img, f"Face: {status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Eye Gaze
        y_offset += line_height
        color = (0, 255, 0) if "Center" in self.eye_status or "●" in self.eye_status else (0, 165, 255)
        cv2.putText(img, f"Eyes: {self.eye_status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Head Pose
        y_offset += line_height
        color = (0, 255, 0) if "Straight" in self.head_status else (0, 165, 255)
        cv2.putText(img, f"Head: {self.head_status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Person Count
        y_offset += line_height
        if self.person_count == 1:
            color = (0, 255, 0)
            status = f"{self.person_count} Person ✓"
        elif self.person_count == 0:
            color = (0, 0, 255)
            status = "No Person ✗"
        else:
            color = (0, 0, 255)
            status = f"{self.person_count} People ✗"
        cv2.putText(img, f"Count: {status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Phone Detection
        y_offset += line_height
        if self.phone_detected:
            color = (0, 0, 255)
            status = "Phone Detected! ⚠"
        else:
            color = (0, 255, 0)
            status = "No Phone ✓"
        cv2.putText(img, f"Phone: {status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Alert Level Box
        alert_colors = {
            "NORMAL": (0, 255, 0),
            "WARNING": (0, 165, 255),
            "ALERT": (0, 0, 255)
        }
        alert_color = alert_colors.get(self.alert_level, (255, 255, 255))
        
        cv2.rectangle(img, (w - 200, 70), (w - 20, 120), alert_color, -1)
        cv2.putText(img, self.alert_level, (w - 180, 100),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
        
        # Active Alerts (bottom of screen)
        if self.alerts:
            alert_y = h - 60
            cv2.rectangle(img, (10, h - 70), (w - 10, h - 10), (0, 0, 255), -1)
            alert_text = " | ".join(self.alerts[:3])  # Show max 3 alerts
            cv2.putText(img, f"⚠ ALERTS: {alert_text}", (20, alert_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return img
    
    def update_alert_level(self):
        """Update alert level based on detections"""
        self.alerts = []
        
        if not self.face_detected:
            self.alerts.append("NO FACE")
        
        if self.person_count == 0:
            self.alerts.append("NO PERSON")
        elif self.person_count > 1:
            self.alerts.append("MULTIPLE PEOPLE")
        
        if self.phone_detected:
            self.alerts.append("PHONE DETECTED")
        
        if "Looking Left" in self.eye_status or "Looking Right" in self.eye_status:
            self.alerts.append("EYE MOVEMENT")
        
        if "Down" in self.head_status or "Up" in self.head_status:
            self.alerts.append("HEAD MOVEMENT")
        
        # Set alert level
        if len(self.alerts) >= 3 or self.phone_detected or self.person_count != 1:
            self.alert_level = "ALERT"
        elif len(self.alerts) >= 1:
            self.alert_level = "WARNING"
        else:
            self.alert_level = "NORMAL"
    
    def run(self):
        """Main loop for integrated dashboard"""
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                print("Error: Lost camera connection")
                break
            
            # Reset status for this frame
            self.reset_status()
            
            # Detect faces
            faces = find_faces(frame, face_model)
            
            if len(faces) > 0:
                self.face_detected = True
                
                for face in faces:
                    # Draw face rectangle
                    x, y, x1, y1 = face
                    cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)
                    
                    # Detect facial landmarks
                    marks = detect_marks(frame, landmark_model, face)
                    
                    # Draw landmark points
                    for mark in marks:
                        cv2.circle(frame, (mark[0], mark[1]), 2, (0, 255, 255), -1)
                    
                    # Eye gaze detection
                    self.eye_status = self.detect_eye_gaze(frame, marks)
                    
                    # Head pose detection
                    self.head_status = self.detect_head_pose(frame, marks)
            
            # Person and phone detection (every 5 frames to improve performance)
            if frame_count % 5 == 0:
                self.person_count, self.phone_detected = self.detect_objects(frame)
            
            # Update alert level
            self.update_alert_level()
            
            # Draw dashboard overlay
            frame = self.draw_dashboard(frame)
            
            # Show FPS
            cv2.putText(frame, f"FPS: {int(self.cap.get(cv2.CAP_PROP_FPS))}", 
                       (frame.shape[1] - 100, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display
            cv2.imshow("Proctoring AI - Integrated Dashboard", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nShutting down...")
                break
            elif key == ord('s'):
                # Save screenshot
                filename = f"proctoring_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved: {filename}")
            
            frame_count += 1
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Dashboard closed.")


def main():
    print("="*60)
    print(" "*10 + "INTEGRATED PROCTORING AI DASHBOARD")
    print("="*60)
    print("\nInitializing...")
    
    try:
        dashboard = ProctoringDashboard(video_source=0)
        dashboard.run()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your camera is connected")
        print("2. Close other applications using the camera")
        print("3. Try running: python test_camera.py")


if __name__ == "__main__":
    main()
