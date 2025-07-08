import pyaudio
import struct
import pvporcupine
import speech_recognition as sr
import cv2
import requests
import io
import time
from PIL import Image
import config

class IronManClient:
    def __init__(self):
        self.porcupine = None
        self.audio_stream = None
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
        self.setup_audio()
        
    def setup_audio(self):
        """Initialize Porcupine wake word detection and audio stream"""
        try:
            self.porcupine = pvporcupine.create(
                access_key=config.PORCUPINE_ACCESS_KEY,
                keywords=config.WAKE_WORDS
            )
            
            audio = pyaudio.PyAudio()
            self.audio_stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=config.CHUNK_SIZE
            )
            
            print(f"Listening for wake words: {config.WAKE_WORDS}")
            
        except Exception as e:
            print(f"Error setting up audio: {e}")
            print("Make sure you have a valid Porcupine access key in config.py")
    
    def capture_image(self):
        """Capture image from camera"""
        ret, frame = self.camera.read()
        if ret:
            # Resize image for faster processing
            frame = cv2.resize(frame, (config.IMAGE_WIDTH, config.IMAGE_HEIGHT))
            return frame
        return None
    
    def listen_for_wake_word(self):
        """Listen for wake word using Porcupine"""
        if not self.porcupine or not self.audio_stream:
            return False
            
        try:
            audio_data = self.audio_stream.read(config.CHUNK_SIZE, exception_on_overflow=False)
            audio_frame = struct.unpack_from("h" * config.CHUNK_SIZE, audio_data)
            
            keyword_index = self.porcupine.process(audio_frame)
            if keyword_index >= 0:
                print(f"Wake word detected: {config.WAKE_WORDS[keyword_index]}")
                return True
                
        except Exception as e:
            print(f"Error in wake word detection: {e}")
            
        return False
    
    def listen_for_command(self, timeout=5):
        """Listen for voice command after wake word"""
        try:
            print("Listening for command...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            command = self.recognizer.recognize_google(audio).lower()
            print(f"Command heard: {command}")
            return command
            
        except sr.WaitTimeoutError:
            print("No command heard within timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand the command")
            return None
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None
    
    def parse_command(self, command):
        """Parse command to extract device and action"""
        if not command:
            return None, None
            
        # Simple command parsing - look for "turn [device] on/off"
        words = command.split()
        
        if "turn" in words:
            turn_index = words.index("turn")
            
            # Look for "on" or "off"
            action = None
            if "on" in words:
                action = "on"
                action_index = words.index("on")
            elif "off" in words:
                action = "off"
                action_index = words.index("off")
            
            if action and turn_index < action_index:
                # Extract device name between "turn" and "on/off"
                device_words = words[turn_index + 1:action_index]
                device = " ".join(device_words).strip()
                return device, action
        
        return None, None
    
    def send_to_server(self, image, device, action):
        """Send image and command to server"""
        try:
            # Convert image to bytes
            _, img_encoded = cv2.imencode('.jpg', image)
            img_bytes = img_encoded.tobytes()
            
            files = {'image': ('image.jpg', img_bytes, 'image/jpeg')}
            data = {'device': device, 'action': action}
            
            print(f"Sending to server: {device} -> {action}")
            response = requests.post(config.API_ENDPOINT, files=files, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Server response: {result.get('message', 'Success')}")
                return True
            else:
                print(f"Server error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending to server: {e}")
            return False
    
    def run(self):
        """Main client loop"""
        print("VisualAssistant Client Started!")
        print("Say a wake word followed by 'turn [device] on/off'")
        
        try:
            while True:
                # Listen for wake word
                if self.listen_for_wake_word():
                    time.sleep(0.2)  # Brief pause after wake word
                    
                    # Listen for command
                    command = self.listen_for_command()
                    device, action = self.parse_command(command)
                    
                    if device and action:
                        # Capture image
                        image = self.capture_image()
                        if image is not None:
                            # Send to server
                            self.send_to_server(image, device, action)
                        else:
                            print("Failed to capture image")
                    else:
                        print("Could not parse command. Try: 'turn [device] on/off'")

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage. Don't freeze my laptop :/
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.audio_stream:
            self.audio_stream.close()
        if self.porcupine:
            self.porcupine.delete()
        if self.camera:
            self.camera.release()

if __name__ == "__main__":
    client = IronManClient()
    client.run()
