"""
Enhanced Audio Monitor - Integrates recording, transcription, and keyword analysis
Based on audio_part.py with improvements for real-time monitoring
"""

import speech_recognition as sr
import pyaudio
import wave
import time
import threading
import os
from datetime import datetime
from collections import deque
import numpy as np

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️ NLTK not available - install with: pip install nltk")


class EnhancedAudioMonitor:
    """Enhanced audio monitoring with recording and analysis"""
    
    def __init__(self, output_dir="audio_recordings"):
        self.output_dir = output_dir
        self.is_running = False
        self.recording_thread = None
        self.analysis_thread = None
        
        # Audio settings
        self.chunk = 2048
        self.sample_format = pyaudio.paInt16
        self.channels = 1  # Mono for better compatibility
        self.fs = 44100
        self.record_seconds = 10  # Record in 10-second chunks
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize PyAudio
        try:
            self.p = pyaudio.PyAudio()
            print("✓ PyAudio initialized")
        except Exception as e:
            print(f"❌ Error initializing PyAudio: {e}")
            self.p = None
        
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        
        # Suspicious keywords (from audio_part.py concept)
        self.suspicious_keywords = [
            'answer', 'question', 'help', 'tell', 'what', 'how',
            'google', 'search', 'look', 'check', 'phone', 'call',
            'message', 'chat', 'send', 'share', 'whatsapp', 'text'
        ]
        
        # Detection results
        self.transcriptions = []
        self.violations = []
        self.recording_count = 0
        
        # Question paper keywords (can be loaded from file)
        self.question_keywords = []
        
        # Download NLTK data if available
        if NLTK_AVAILABLE:
            try:
                stopwords.words('english')
            except LookupError:
                print("Downloading NLTK stopwords...")
                nltk.download('stopwords', quiet=True)
                nltk.download('punkt', quiet=True)
    
    def load_question_paper(self, filepath):
        """Load question paper and extract keywords"""
        if not NLTK_AVAILABLE:
            print("⚠️ NLTK not available - cannot analyze questions")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = f.read()
            
            # Remove stop words
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(data.lower())
            self.question_keywords = [w for w in word_tokens if w not in stop_words and len(w) > 3]
            
            print(f"✓ Loaded {len(self.question_keywords)} keywords from question paper")
        except Exception as e:
            print(f"❌ Error loading question paper: {e}")
    
    def start_monitoring(self):
        """Start audio monitoring and recording"""
        if not self.p:
            print("❌ PyAudio not initialized")
            return False
        
        if self.is_running:
            return True
        
        self.is_running = True
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        
        print("🎤 Enhanced audio monitoring started")
        return True
    
    def stop_monitoring(self):
        """Stop audio monitoring"""
        self.is_running = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        print("⏹️ Audio monitoring stopped")
    
    def _recording_loop(self):
        """Continuous recording and analysis loop"""
        try:
            # Open stream
            stream = self.p.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True
            )
            
            print("✓ Audio stream opened - recording...")
            
            while self.is_running:
                try:
                    # Record audio chunk
                    filename = self._record_chunk(stream)
                    
                    # Analyze in separate thread to avoid blocking
                    analysis_thread = threading.Thread(
                        target=self._analyze_recording,
                        args=(filename,),
                        daemon=True
                    )
                    analysis_thread.start()
                    
                except Exception as e:
                    print(f"❌ Recording error: {e}")
                    time.sleep(1)
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"❌ Could not start recording: {e}")
    
    def _record_chunk(self, stream):
        """Record a single audio chunk"""
        frames = []
        
        # Record for specified seconds
        for i in range(0, int(self.fs / self.chunk * self.record_seconds)):
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                print(f"⚠️ Audio overflow: {e}")
                continue
        
        # Save to WAV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"recording_{timestamp}.wav")
        
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            self.recording_count += 1
            print(f"✓ Recorded: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return None
    
    def _analyze_recording(self, filename):
        """Analyze recorded audio for speech and keywords"""
        if not filename or not os.path.exists(filename):
            return
        
        try:
            # Transcribe audio
            with sr.AudioFile(filename) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            try:
                # Multi-language transcription (Hindi + English)
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
                
                if not text:
                    print(f"   (No speech detected in {os.path.basename(filename)})")
                    return
                
                print(f"📝 Transcribed ({detected_language}): {text}")
                
                self.transcriptions.append({
                    'timestamp': datetime.now(),
                    'text': text,
                    'language': detected_language,
                    'file': filename
                })
                
                # Check for suspicious keywords
                text_lower = text.lower()
                found_suspicious = [kw for kw in self.suspicious_keywords if kw in text_lower]
                
                # Add Hindi suspicious keywords
                hindi_suspicious = ['jawab', 'uttar', 'madad', 'kya', 'kaise', 'batao', 'bata']
                found_hindi = [kw for kw in hindi_suspicious if kw in text_lower]
                found_suspicious.extend(found_hindi)
                
                if found_suspicious:
                    violation = {
                        'timestamp': datetime.now(),
                        'type': 'SUSPICIOUS_SPEECH',
                        'keywords': found_suspicious,
                        'language': detected_language,
                        'text': text
                    }
                    self.violations.append(violation)
                    print(f"⚠️ SUSPICIOUS: Found keywords: {found_suspicious}")
                
                # Check against question paper
                if self.question_keywords and NLTK_AVAILABLE:
                    words = word_tokenize(text_lower)
                    common = set(words) & set(self.question_keywords)
                    
                    if len(common) > 2:  # More than 2 matching words
                        violation = {
                            'timestamp': datetime.now(),
                            'type': 'QUESTION_MATCH',
                            'matches': list(common),
                            'language': detected_language,
                            'text': text
                        }
                        self.violations.append(violation)
                        print(f"⚠️ QUESTION MATCH: {common}")
                
                # Save transcription
                self._save_transcription(f"[{detected_language}] {text}")
                
            except sr.UnknownValueError:
                print(f"   (No speech detected in {os.path.basename(filename)})")
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
            
            # Delete audio file to save space (optional)
            try:
                os.remove(filename)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
    
    def _save_transcription(self, text):
        """Save transcription to text file"""
        try:
            filepath = os.path.join(self.output_dir, "transcriptions.txt")
            with open(filepath, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {text}\n")
        except Exception as e:
            print(f"❌ Error saving transcription: {e}")
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'recording_count': self.recording_count,
            'transcription_count': len(self.transcriptions),
            'violation_count': len(self.violations),
            'recent_transcriptions': self.transcriptions[-5:] if self.transcriptions else [],
            'recent_violations': self.violations[-5:] if self.violations else []
        }
    
    def get_violations(self):
        """Get all violations"""
        return self.violations
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()
        if self.p:
            self.p.terminate()


# Test function
def test_enhanced_monitor():
    """Test the enhanced audio monitor"""
    print("=" * 60)
    print("ENHANCED AUDIO MONITOR TEST")
    print("=" * 60)
    
    monitor = EnhancedAudioMonitor()
    
    # Optional: Load question paper
    question_file = "paper.txt"
    if os.path.exists(question_file):
        monitor.load_question_paper(question_file)
    
    print("\nStarting monitoring for 30 seconds...")
    print("SPEAK NOW to test detection\n")
    
    monitor.start_monitoring()
    
    try:
        # Monitor for 30 seconds
        for i in range(30):
            time.sleep(1)
            if (i + 1) % 10 == 0:
                status = monitor.get_status()
                print(f"\n--- Status at {i+1}s ---")
                print(f"Recordings: {status['recording_count']}")
                print(f"Transcriptions: {status['transcription_count']}")
                print(f"Violations: {status['violation_count']}")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    
    monitor.stop_monitoring()
    
    # Show results
    status = monitor.get_status()
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total Recordings: {status['recording_count']}")
    print(f"Total Transcriptions: {status['transcription_count']}")
    print(f"Total Violations: {status['violation_count']}")
    
    if status['recent_violations']:
        print("\nViolations Detected:")
        for v in status['recent_violations']:
            print(f"  - {v['type']}: {v.get('keywords', v.get('matches', []))}")
    
    monitor.cleanup()


if __name__ == '__main__':
    test_enhanced_monitor()
