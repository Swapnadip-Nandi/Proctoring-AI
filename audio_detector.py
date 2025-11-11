"""
Real-time Audio Detection Module for Proctoring AI
Monitors audio for suspicious speech and conversation patterns
"""

import threading
import queue
import time
import numpy as np
from collections import deque

try:
    import speech_recognition as sr
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    sr = None
    pyaudio = None
    print("Warning: speech_recognition or pyaudio not installed. Audio detection disabled.")
    print("Install with: pip install SpeechRecognition pyaudio")


class AudioDetector:
    """Real-time audio detection for proctoring"""
    
    def __init__(self):
        global AUDIO_AVAILABLE
        
        self.is_running = False
        self.audio_thread = None
        self.volume_thread = None
        self.audio_queue = queue.Queue()
        self.detection_status = {
            'audio_detected': False,
            'speech_detected': False,
            'volume_level': 0,
            'last_speech': None,
            'suspicious_keywords': [],
            'conversation_detected': False
        }
        
        # Suspicious keywords that might indicate cheating
        self.suspicious_keywords = [
            'answer', 'question', 'help', 'tell', 'what', 'how',
            'google', 'search', 'look', 'check', 'phone', 'call',
            'message', 'chat', 'send', 'share'
        ]
        
        # Volume history for conversation detection
        self.volume_history = deque(maxlen=10)
        
        if not AUDIO_AVAILABLE:
            print("⚠️ Audio detection not available - missing dependencies")
            return
        
        try:
            # Initialize recognizer with better settings
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 200  # LOWER = MORE SENSITIVE
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 0.5  # Shorter pause
            self.recognizer.phrase_threshold = 0.3  # Detect shorter phrases
            self.recognizer.non_speaking_duration = 0.3
            
            # Initialize microphone
            self.microphone = sr.Microphone()
            
            # Initialize PyAudio for direct volume monitoring
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Calibrate microphone for ambient noise
            print("🎤 Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print(f"✓ Microphone calibrated (threshold: {self.recognizer.energy_threshold})")
            
        except Exception as e:
            print(f"❌ Error initializing audio detector: {e}")
            AUDIO_AVAILABLE = False

        self.volume_history = deque(maxlen=50)  # Last 5 seconds at 10 readings/sec
        
        # PyAudio for direct volume monitoring
        self.pyaudio_instance = None
        
        if not AUDIO_AVAILABLE:
            self.recognizer = None
            self.microphone = None
            print("Audio detection is disabled - required packages not installed")
            return
            
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize PyAudio for volume monitoring
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
        except Exception as e:
            print(f"Could not initialize PyAudio: {e}")
            self.pyaudio_instance = None
        
        # Adjust for ambient noise
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                print("Calibrating for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.recognizer.energy_threshold = 300  # More sensitive
                self.recognizer.dynamic_energy_threshold = True
                print("Audio detector initialized successfully!")
        except Exception as e:
            print(f"Could not initialize microphone: {e}")
            self.microphone = None
            AUDIO_AVAILABLE = False
    
    def start(self):
        """Start audio monitoring"""
        global AUDIO_AVAILABLE
        
        if not AUDIO_AVAILABLE or self.microphone is None:
            print("Audio detection not available")
            return False
        
        if self.is_running:
            return True
        
        self.is_running = True
        
        # Start speech detection thread
        self.audio_thread = threading.Thread(target=self._audio_monitoring_loop, daemon=True)
        self.audio_thread.start()
        
        # Start simple volume monitoring thread for continuous display
        self.volume_thread = threading.Thread(target=self._volume_monitoring_loop, daemon=True)
        self.volume_thread.start()
        
        print("Audio monitoring started (speech + volume)")
        return True
    
    def stop(self):
        """Stop audio monitoring"""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
        if self.volume_thread:
            self.volume_thread.join(timeout=2)
        print("Audio monitoring stopped")
    
    def _volume_monitoring_loop(self):
        """Simple continuous volume monitoring using PyAudio"""
        if not self.pyaudio_instance:
            return
        
        stream = None
        try:
            # Open audio stream for volume monitoring with error handling
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=2048,
                input_device_index=None  # Use default microphone
            )
            
            print("✓ Volume monitoring started (listening for audio)...")
            consecutive_silent = 0
            
            while self.is_running:
                try:
                    # Read audio data
                    data = stream.read(2048, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Calculate RMS volume (more accurate)
                    rms = np.sqrt(np.mean(audio_data**2))
                    volume = int((rms / 32768.0) * 100)
                    
                    # Amplify quiet sounds for better visibility
                    if volume > 0 and volume < 10:
                        volume = int(volume * 1.5)  # Boost quiet sounds
                    
                    # Update volume level with smoothing
                    current_volume = self.detection_status.get('volume_level', 0)
                    smooth_volume = int((current_volume * 0.6) + (volume * 0.4))
                    
                    self.detection_status['volume_level'] = smooth_volume
                    
                    # Detect audio presence with lower threshold
                    if smooth_volume > 2:  # VERY LOW threshold (2%)
                        self.detection_status['audio_detected'] = True
                        consecutive_silent = 0
                    else:
                        consecutive_silent += 1
                        if consecutive_silent > 10:  # 1 second of silence
                            self.detection_status['audio_detected'] = False
                    
                    time.sleep(0.1)  # Update 10 times per second
                    
                except IOError as e:
                    print(f"⚠️ Audio input overflow (normal): {e}")
                    time.sleep(0.1)
                except Exception as e:
                    print(f"❌ Volume monitoring error: {e}")
                    time.sleep(0.5)
            
            if stream:
                stream.stop_stream()
                stream.close()
            
        except Exception as e:
            print(f"❌ Could not start volume monitoring: {e}")
            print("   Check microphone permissions and try again")

    
    def _audio_monitoring_loop(self):
        """Continuous audio monitoring loop"""
        print("Starting audio monitoring loop...")
        
        # Configure recognizer for better sensitivity
        self.recognizer.energy_threshold = 300  # Lower = more sensitive
        self.recognizer.dynamic_energy_threshold = True
        
        while self.is_running:
            try:
                with self.microphone as source:
                    # Very short timeout for responsive volume monitoring
                    try:
                        audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=3)
                    except sr.WaitTimeoutError:
                        # Update volume even on timeout
                        self.detection_status['volume_level'] = max(0, self.detection_status.get('volume_level', 0) - 2)
                        continue
                    audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=3)
                    
                    # Calculate volume level (RMS) - More sensitive calculation
                    audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_data**2))
                    volume_level = int((rms / 32768.0) * 100)  # Normalize to 0-100
                    
                    # Apply minimum volume boost for visibility
                    if volume_level > 0:
                        volume_level = max(volume_level, 5)  # Show at least 5% if any sound
                    
                    self.detection_status['volume_level'] = volume_level
                    self.volume_history.append(volume_level)
                    
                    # More sensitive threshold for detecting sound
                    if volume_level > 3:  # Lower threshold - more sensitive
                        self.detection_status['audio_detected'] = True
                        
                        # Try to recognize speech if volume is significant
                        if volume_level > 8:
                            self._process_speech(audio)
                    else:
                        self.detection_status['audio_detected'] = False
                        self.detection_status['speech_detected'] = False
                    
                    # Detect conversation patterns (varying volume levels)
                    self._detect_conversation()
                    
            except sr.WaitTimeoutError:
                # No audio detected in timeout period - keep last volume
                if self.detection_status['volume_level'] > 0:
                    self.detection_status['volume_level'] = max(0, self.detection_status['volume_level'] - 1)
                self.detection_status['audio_detected'] = False
            except Exception as e:
                print(f"Audio monitoring error: {e}")
                time.sleep(0.3)
    
    def _process_speech(self, audio):
        """Process audio for speech recognition with multi-language support"""
        try:
            # Try Hindi first, then English
            languages = [
                ('hi-IN', 'Hindi'),
                ('en-IN', 'English (India)'),
                ('en-US', 'English (US)')
            ]
            
            text = None
            detected_language = None
            
            for lang_code, lang_name in languages:
                try:
                    text = self.recognizer.recognize_google(audio, language=lang_code)
                    if text:
                        detected_language = lang_name
                        break
                except sr.UnknownValueError:
                    continue
                except Exception:
                    continue
            
            if text:
                self.detection_status['speech_detected'] = True
                self.detection_status['last_speech'] = text.lower()
                self.detection_status['detected_language'] = detected_language
                
                # Check for suspicious keywords (works in any language)
                detected_keywords = []
                text_lower = text.lower()
                
                # English suspicious keywords
                for keyword in self.suspicious_keywords:
                    if keyword in text_lower:
                        detected_keywords.append(keyword)
                
                # Hindi suspicious keywords (romanized)
                hindi_suspicious = [
                    'jawab', 'uttar', 'madad', 'help', 'kya', 'kaise',
                    'google', 'phone', 'message', 'batao', 'bata'
                ]
                for keyword in hindi_suspicious:
                    if keyword in text_lower:
                        detected_keywords.append(keyword)
                
                self.detection_status['suspicious_keywords'] = detected_keywords
                
                print(f"🗣️ Speech detected ({detected_language}): {text}")
                if detected_keywords:
                    print(f"⚠️ Suspicious keywords: {detected_keywords}")
                
        except sr.UnknownValueError:
            # Speech was unintelligible in all languages
            self.detection_status['speech_detected'] = False
            self.detection_status['last_speech'] = None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service: {e}")
    
    def _detect_conversation(self):
        """Detect if there's a conversation pattern (multiple speakers)"""
        if len(self.volume_history) < 20:
            return
        
        # Calculate variance in volume levels
        volume_array = np.array(list(self.volume_history))
        variance = np.var(volume_array)
        
        # High variance with significant volume indicates potential conversation
        mean_volume = np.mean(volume_array)
        if variance > 100 and mean_volume > 15:
            self.detection_status['conversation_detected'] = True
        else:
            self.detection_status['conversation_detected'] = False
    
    def get_status(self):
        """Get current detection status"""
        return self.detection_status.copy()
    
    def is_suspicious(self):
        """Check if current audio status is suspicious"""
        status = self.detection_status
        return (
            status['speech_detected'] or
            len(status['suspicious_keywords']) > 0 or
            status['conversation_detected']
        )


# Global instance for easy import
audio_detector = None

def get_audio_detector():
    """Get or create audio detector instance"""
    global audio_detector
    if audio_detector is None:
        audio_detector = AudioDetector()
    return audio_detector


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎤 AUDIO DETECTOR TEST")
    print("="*60 + "\n")
    
    detector = AudioDetector()
    
    if not AUDIO_AVAILABLE:
        print("❌ Audio detection not available")
        print("Please install required packages:")
        print("  pip install SpeechRecognition pyaudio")
        exit(1)
    
    print("Starting audio monitoring for 30 seconds...")
    print("Try speaking to test detection\n")
    
    detector.start()
    
    try:
        for i in range(60):  # 30 seconds
            time.sleep(0.5)
            status = detector.get_status()
            
            # Clear screen and show status
            print(f"\r[{i//2 + 1}/30s] "
                  f"Audio: {'🔊' if status['audio_detected'] else '🔇'} | "
                  f"Speech: {'🗣️' if status['speech_detected'] else '❌'} | "
                  f"Volume: {status['volume_level']}% | "
                  f"Conversation: {'⚠️' if status['conversation_detected'] else '✓'} | "
                  f"Suspicious: {'🚨' if detector.is_suspicious() else '✓'}",
                  end='', flush=True)
            
            if status['last_speech']:
                print(f"\n  > Heard: \"{status['last_speech']}\"", end='')
            if status['suspicious_keywords']:
                print(f"\n  ⚠️ Keywords: {status['suspicious_keywords']}", end='')
    
    except KeyboardInterrupt:
        print("\n\nStopping test...")
    finally:
        detector.stop()
        print("\n\nAudio detector test completed!")
