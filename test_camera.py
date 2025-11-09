"""
Quick camera test script
"""
import cv2
import sys

print("Testing camera access...")
print("Available camera indices to try: 0, 1, 2")
print()

# Try different camera indices
for i in range(3):
    print(f"Trying camera index {i}...")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ Camera {i} is working!")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            
            # Show a test window
            cv2.imshow(f'Camera {i} Test - Press any key', frame)
            print(f"  Showing test frame... press any key to continue")
            cv2.waitKey(2000)  # Show for 2 seconds or until key press
            cv2.destroyAllWindows()
        else:
            print(f"✗ Camera {i} opened but cannot read frames")
        cap.release()
    else:
        print(f"✗ Camera {i} cannot be opened")
    print()

print("\nRecommendation:")
print("Use the camera index that worked in your modules.")
print("If no camera worked, check:")
print("  1. Camera is connected")
print("  2. Camera permissions are enabled")
print("  3. No other application is using the camera")
