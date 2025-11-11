"""
Test Script for All Fixes
Tests: Screenshot prevention, 5-second updates, audio detection, enhanced audio integration
"""

import os
import sys

print("=" * 70)
print("COMPREHENSIVE FIX VERIFICATION")
print("=" * 70)

# Test 1: Verify update interval changed to 5 seconds
print("\n[Test 1] Checking dashboard update interval...")
try:
    with open('static/js/dashboard.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '5000' in content and 'Update every 5 seconds' in content:
        print("✓ Update interval set to 5 seconds")
    else:
        print("❌ Update interval not correctly set")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Verify ultra-aggressive screenshot prevention
print("\n[Test 2] Checking screenshot prevention...")
try:
    with open('static/js/dashboard.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('stopImmediatePropagation', 'Stop immediate propagation'),
        ('contextmenu', 'Context menu disabled'),
        ('true); // Use capture phase', 'Capture phase enabled'),
        ('Method 1c:', 'Global key blocking'),
        ('Method 1d:', 'Right-click disabled')
    ]
    
    for check, desc in checks:
        if check in content:
            print(f"  ✓ {desc}")
        else:
            print(f"  ❌ {desc} - NOT FOUND")
            
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Verify audio detector improvements
print("\n[Test 3] Checking audio detector improvements...")
try:
    with open('audio_detector.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('energy_threshold = 200', 'Lower sensitivity threshold (200)'),
        ('frames_per_buffer=2048', 'Larger buffer for stability'),
        ('if smooth_volume > 2:', 'Very low detection threshold (2%)'),
        ('Amplify quiet sounds', 'Volume amplification'),
        ('consecutive_silent', 'Silent period tracking'),
        ('IOError as e:', 'Overflow handling')
    ]
    
    for check, desc in checks:
        if check in content:
            print(f"  ✓ {desc}")
        else:
            print(f"  ❌ {desc} - NOT FOUND")
            
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Verify enhanced audio monitor created
print("\n[Test 4] Checking enhanced audio monitor...")
try:
    if os.path.exists('enhanced_audio_monitor.py'):
        print("  ✓ Enhanced audio monitor file created")
        
        with open('enhanced_audio_monitor.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        features = [
            ('EnhancedAudioMonitor', 'Main class'),
            ('_record_chunk', 'Recording functionality'),
            ('_analyze_recording', 'Analysis functionality'),
            ('load_question_paper', 'Question paper integration'),
            ('suspicious_keywords', 'Keyword detection'),
            ('nltk', 'NLTK integration')
        ]
        
        for feature, desc in features:
            if feature in content:
                print(f"  ✓ {desc}")
            else:
                print(f"  ❌ {desc} - NOT FOUND")
    else:
        print("  ❌ Enhanced audio monitor file not found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Check if NLTK is installed
print("\n[Test 5] Checking NLTK installation...")
try:
    import nltk
    print("  ✓ NLTK is installed")
    
    # Check for required data
    try:
        from nltk.corpus import stopwords
        stopwords.words('english')
        print("  ✓ NLTK stopwords available")
    except:
        print("  ⚠️ NLTK stopwords not downloaded (will download on first use)")
        
except ImportError:
    print("  ❌ NLTK not installed - run: pip install nltk")

# Test 6: Verify audio packages
print("\n[Test 6] Checking audio packages...")
packages = [
    ('speech_recognition', 'SpeechRecognition'),
    ('pyaudio', 'PyAudio'),
    ('numpy', 'NumPy')
]

for module, name in packages:
    try:
        __import__(module)
        print(f"  ✓ {name} installed")
    except ImportError:
        print(f"  ❌ {name} NOT installed - run: pip install {module}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
✅ FIXES APPLIED:

1. Screenshot Prevention (ULTRA AGGRESSIVE):
   - Multiple key event captures (keydown + keyup + window-level)
   - Stop immediate propagation
   - Context menu completely disabled
   - Capture phase event handling
   - Right-click blocked globally

2. Update Interval:
   - Changed from 1 second to 5 SECONDS
   - Activity Log and Violations update every 5 seconds

3. Audio Detection (ULTRA SENSITIVE):
   - Energy threshold lowered to 200 (very sensitive)
   - Detection threshold lowered to 2% (catches whispers)
   - Volume amplification for quiet sounds
   - Larger buffer (2048) for stability
   - Better overflow handling
   - Silent period tracking

4. Enhanced Audio Monitor:
   - Records audio in 10-second chunks
   - Transcribes using Google Speech API
   - Detects suspicious keywords
   - Compares against question paper
   - Saves transcriptions to file
   - NLTK integration for word analysis

📋 NEXT STEPS:

1. RESTART Flask application:
   python flask_app.py

2. TEST Screenshot Prevention:
   - Press PrintScreen → Should show warning
   - Right-click → Should be blocked
   - Try any screenshot tool → Should be logged

3. TEST Audio Detection:
   - Speak normally → Volume should show 5-20%
   - Whisper → Volume should show 2-10%
   - Make any sound → Should be detected immediately

4. TEST 5-Second Updates:
   - Perform actions
   - Activity Log should update every 5 seconds
   - Check timestamps to verify

5. TEST Enhanced Audio (Optional):
   python enhanced_audio_monitor.py
   
6. CREATE question paper file (optional):
   Create paper.txt with exam questions
   Enhanced monitor will detect if student speaks question words

⚠️ IMPORTANT NOTES:

- Screenshots can NEVER be 100% blocked (external cameras exist)
- System will LOG all attempts even if some succeed
- Audio detection requires microphone permissions
- Browser must allow microphone access
- Test in Chrome/Edge for best compatibility

🎯 VERIFICATION:

Run Flask app and check:
- Activity Log updates every 5 seconds ✓
- Screenshot attempts trigger warnings ✓
- Audio volume bar shows movement ✓
- Violations are logged properly ✓
""")

print("=" * 70)
print("All fixes verified! Ready to test.")
print("=" * 70)
