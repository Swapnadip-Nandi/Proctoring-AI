"""
Advanced Audio Analysis Module
Extends audio_detector.py with question-answer comparison
Based on the original audio_part.py with enhancements
"""

import speech_recognition as sr
import pyaudio
import wave
import time
import threading
import os
from collections import deque

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    import nltk
    
    # Download required NLTK data (only once)
    try:
        stopwords.words('english')
    except LookupError:
        print("Downloading NLTK stopwords data...")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not installed. Advanced text analysis disabled.")
    print("Install with: pip install nltk")


class AdvancedAudioAnalyzer:
    """
    Advanced audio analysis for exam proctoring
    Compares student speech with exam questions to detect cheating
    """
    
    def __init__(self, question_file=None):
        self.recognizer = sr.Recognizer()
        self.pyaudio_instance = pyaudio.PyAudio()
        self.is_recording = False
        self.recording_thread = None
        self.transcripts = []
        self.question_keywords = []
        
        # Recording parameters
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 2
        self.sample_rate = 44100
        self.record_duration = 10  # seconds per chunk
        
        # Load question file if provided
        if question_file and os.path.exists(question_file):
            self.load_questions(question_file)
    
    def load_questions(self, question_file):
        """Load and process exam questions"""
        if not NLTK_AVAILABLE:
            print("Cannot load questions - NLTK not available")
            return
        
        try:
            with open(question_file, 'r', encoding='utf-8') as f:
                questions_text = f.read()
            
            # Tokenize and remove stop words
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(questions_text.lower())
            
            self.question_keywords = [
                word for word in word_tokens 
                if word.isalnum() and word not in stop_words
            ]
            
            print(f"✓ Loaded {len(self.question_keywords)} keywords from questions")
            
        except Exception as e:
            print(f"Error loading questions: {e}")
    
    def record_audio_chunk(self, filename):
        """Record a single audio chunk"""
        try:
            stream = self.pyaudio_instance.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.sample_rate,
                frames_per_buffer=self.chunk,
                input=True
            )
            
            frames = []
            
            # Record for specified duration
            for i in range(0, int(self.sample_rate / self.chunk * self.record_duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            # Save as WAV file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.sample_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            stream.stop_stream()
            stream.close()
            
            return True
            
        except Exception as e:
            print(f"Error recording audio: {e}")
            return False
    
    def transcribe_audio(self, audio_file):
        """Convert audio file to text"""
        try:
            with sr.AudioFile(audio_file) as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
            
            try:
                text = self.recognizer.recognize_google(audio)
                
                # Clean up audio file
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                
                return text
                
            except sr.UnknownValueError:
                # Could not understand audio
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                return None
                
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                return None
                
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    
    def analyze_speech(self, transcript):
        """Analyze transcript for suspicious content"""
        if not NLTK_AVAILABLE or not transcript:
            return {
                'suspicious': False,
                'common_words': [],
                'match_percentage': 0
            }
        
        try:
            # Tokenize and remove stop words from transcript
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(transcript.lower())
            
            transcript_keywords = [
                word for word in word_tokens 
                if word.isalnum() and word not in stop_words
            ]
            
            # Find common words between questions and speech
            common_words = set(self.question_keywords) & set(transcript_keywords)
            
            # Calculate match percentage
            if len(transcript_keywords) > 0:
                match_percentage = (len(common_words) / len(transcript_keywords)) * 100
            else:
                match_percentage = 0
            
            # Flag as suspicious if >30% match with question keywords
            is_suspicious = match_percentage > 30
            
            return {
                'suspicious': is_suspicious,
                'common_words': list(common_words),
                'match_percentage': round(match_percentage, 2),
                'transcript': transcript,
                'keywords_found': len(common_words)
            }
            
        except Exception as e:
            print(f"Error analyzing speech: {e}")
            return {
                'suspicious': False,
                'common_words': [],
                'match_percentage': 0
            }
    
    def start_monitoring(self, duration_seconds=60, output_file="audio_analysis.txt"):
        """
        Start continuous audio monitoring for specified duration
        
        Args:
            duration_seconds: Total monitoring duration
            output_file: File to save transcripts
        """
        print(f"\n{'='*60}")
        print("ADVANCED AUDIO MONITORING STARTED")
        print(f"{'='*60}\n")
        print(f"Duration: {duration_seconds} seconds")
        print(f"Recording chunks: {self.record_duration} seconds each")
        print(f"Output file: {output_file}\n")
        
        num_chunks = duration_seconds // self.record_duration
        suspicious_count = 0
        
        # Clear output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Audio Analysis Session - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
        
        for i in range(num_chunks):
            print(f"[{i+1}/{num_chunks}] Recording chunk {i+1}...")
            
            # Record audio
            audio_file = f"temp_record_{i}.wav"
            if self.record_audio_chunk(audio_file):
                
                # Transcribe
                print(f"[{i+1}/{num_chunks}] Transcribing...")
                transcript = self.transcribe_audio(audio_file)
                
                if transcript:
                    print(f"[{i+1}/{num_chunks}] Transcript: \"{transcript}\"")
                    
                    # Analyze
                    analysis = self.analyze_speech(transcript)
                    
                    # Log results
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(f"Chunk {i+1} - {time.strftime('%H:%M:%S')}\n")
                        f.write(f"Transcript: {transcript}\n")
                        f.write(f"Suspicious: {analysis['suspicious']}\n")
                        f.write(f"Match: {analysis['match_percentage']}%\n")
                        if analysis['common_words']:
                            f.write(f"Common words: {', '.join(analysis['common_words'][:10])}\n")
                        f.write("-"*60 + "\n\n")
                    
                    if analysis['suspicious']:
                        suspicious_count += 1
                        print(f"  ⚠️  SUSPICIOUS! Match: {analysis['match_percentage']}%")
                        print(f"  Common words: {', '.join(analysis['common_words'][:5])}")
                    else:
                        print(f"  ✓ Normal speech")
                else:
                    print(f"[{i+1}/{num_chunks}] No speech detected")
            
            print()
        
        # Final summary
        print(f"\n{'='*60}")
        print("MONITORING COMPLETE")
        print(f"{'='*60}\n")
        print(f"Total chunks: {num_chunks}")
        print(f"Suspicious chunks: {suspicious_count}")
        print(f"Suspicion rate: {(suspicious_count/num_chunks*100):.1f}%")
        print(f"\nResults saved to: {output_file}\n")
        
        return {
            'total_chunks': num_chunks,
            'suspicious_chunks': suspicious_count,
            'suspicion_rate': (suspicious_count/num_chunks*100) if num_chunks > 0 else 0
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.pyaudio_instance.terminate()
        
        # Remove any remaining temp files
        for i in range(100):
            temp_file = f"temp_record_{i}.wav"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎤 ADVANCED AUDIO ANALYZER TEST")
    print("="*60 + "\n")
    
    # Create analyzer
    analyzer = AdvancedAudioAnalyzer()
    
    # Check if question file exists
    question_file = "paper.txt"
    if os.path.exists(question_file):
        print(f"✓ Loading questions from: {question_file}")
        analyzer.load_questions(question_file)
    else:
        print(f"⚠️  Question file not found: {question_file}")
        print("Creating sample question file...")
        with open(question_file, 'w') as f:
            f.write("What is the capital of France? Who wrote Romeo and Juliet?")
        analyzer.load_questions(question_file)
    
    print("\nStarting audio monitoring...")
    print("Speak naturally during the test.")
    print("Try mentioning words from the questions to trigger alerts.\n")
    
    try:
        # Monitor for 30 seconds (3 chunks of 10 seconds)
        results = analyzer.start_monitoring(duration_seconds=30)
        
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
    finally:
        analyzer.cleanup()
        print("\nCleanup complete!")
