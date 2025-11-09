"""
Standalone demo script to run individual proctoring modules
Usage: python run_demo.py [module_name]
Modules: eye_tracking, head_pose, mouth_opening, person_phone, face_spoofing
"""

import sys
import argparse


def run_eye_tracking():
    """Run eye tracking module with webcam"""
    print("Starting Eye Tracking...")
    print("Press 'q' to quit")
    from eye_tracker import track_eye
    track_eye(video_path=0)


def run_head_pose():
    """Run head pose estimation module with webcam"""
    print("Starting Head Pose Estimation...")
    print("Press 'q' to quit")
    from head_pose_estimation import detect_head_pose
    detect_head_pose(video_path=0)


def run_mouth_opening():
    """Run mouth opening detection module with webcam"""
    print("Starting Mouth Opening Detection...")
    print("Press 'r' to record baseline, then 'q' to quit")
    from mouth_opening_detector import mouth_opening_detector
    mouth_opening_detector(video_path=0)


def run_person_phone():
    """Run person and phone detection module with webcam"""
    print("Starting Person and Phone Detection...")
    print("This may take a moment to download YOLOv3 weights if not present...")
    print("Press 'q' to quit")
    from person_and_phone import detect_phone_and_person
    detect_phone_and_person(video_path=0)


def run_face_spoofing():
    """Run face spoofing detection module with webcam"""
    print("Starting Face Spoofing Detection...")
    print("Press 'q' to quit")
    import subprocess
    subprocess.run([sys.executable, "face_spoofing.py"])


def run_integrated_dashboard():
    """Run integrated dashboard with all modules"""
    print("Starting Integrated Proctoring Dashboard...")
    print("This combines ALL detection modules in one interface!")
    print("Press 'q' to quit, 's' to save screenshot")
    import subprocess
    subprocess.run([sys.executable, "integrated_dashboard.py"])


def main():
    parser = argparse.ArgumentParser(
        description="Run Proctoring AI Modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available modules:
  dashboard       - 🎯 Integrated dashboard with ALL modules (RECOMMENDED!)
  eye_tracking    - Track eye movements and gaze direction
  head_pose       - Detect head pose and orientation
  mouth_opening   - Detect mouth opening during exam
  person_phone    - Detect multiple persons and mobile phones
  face_spoofing   - Detect face spoofing attempts
  all            - Run all modules sequentially

Examples:
  python run_demo.py dashboard       (Best option!)
  python run_demo.py eye_tracking
  python run_demo.py head_pose
  python run_demo.py person_phone
        """
    )
    
    parser.add_argument(
        'module',
        nargs='?',
        default='menu',
        choices=['dashboard', 'eye_tracking', 'head_pose', 'mouth_opening', 'person_phone', 'face_spoofing', 'all', 'menu'],
        help='Module to run'
    )
    
    args = parser.parse_args()
    
    if args.module == 'menu':
        print("\n" + "="*60)
        print(" "*15 + "PROCTORING AI SYSTEM")
        print("="*60)
        print("\nAvailable Modules:\n")
        print("🎯 dashboard       - INTEGRATED DASHBOARD (ALL IN ONE!) ⭐")
        print("="*60)
        print("1. eye_tracking    - Track eye movements and gaze direction")
        print("2. head_pose       - Detect head pose and orientation")
        print("3. mouth_opening   - Detect mouth opening during exam")
        print("4. person_phone    - Detect multiple persons and mobile phones")
        print("5. face_spoofing   - Detect face spoofing attempts")
        print("\n💡 RECOMMENDED: Start with 'dashboard' for best experience!")
        print("\nUsage: python run_demo.py [module_name]")
        print("Example: python run_demo.py dashboard\n")
        print("="*60 + "\n")
        return
    
    modules = {
        'dashboard': run_integrated_dashboard,
        'eye_tracking': run_eye_tracking,
        'head_pose': run_head_pose,
        'mouth_opening': run_mouth_opening,
        'person_phone': run_person_phone,
        'face_spoofing': run_face_spoofing,
    }
    
    if args.module == 'all':
        print("\n" + "="*60)
        print("Running all modules sequentially...")
        print("="*60 + "\n")
        for name, func in modules.items():
            print(f"\n{'='*60}")
            print(f"Module: {name.upper()}")
            print('='*60)
            try:
                func()
            except KeyboardInterrupt:
                print(f"\n{name} interrupted by user")
                continue
            except Exception as e:
                print(f"\nError in {name}: {e}")
                continue
    else:
        try:
            modules[args.module]()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
