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

# Global Porcupine setup (like in max_voice.py)
print("Setting up Porcupine...")
try:
    keyword_paths = ['Hey-Max_en_linux_v3_0_0.ppn']
    
    porcupine_handle = pvporcupine.create(
        access_key=config.PORCUPINE_ACCESS_KEY,
        keyword_paths=keyword_paths
    )
    print("Porcupine created successfully!")
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine_handle.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine_handle.frame_length
    )
    print("Audio stream opened successfully!")
    print(f"Sample rate: {porcupine_handle.sample_rate}, Frame length: {porcupine_handle.frame_length}")
    
except Exception as e:
    print(f"Error setting up Porcupine: {e}")
    porcupine_handle = None
    audio_stream = None
    pa = None

class VisualAssistantClient:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
        
    def capture_image(self):
        """Capture image from camera"""
        ret, frame = self.camera.read()
        if ret:
            # Resize image for faster processing
            frame = cv2.resize(frame, (config.IMAGE_WIDTH, config.IMAGE_HEIGHT))
            return frame
        return None
    
    def listen_for_wake_word(self):
        """Listen for wake word using Porcupine (exactly like max_voice.py)"""
        global porcupine_handle, audio_stream
        
        if not porcupine_handle or not audio_stream:
            return False
            
        try:
            # Exact same pattern as max_voice.py
            pcm = audio_stream.read(porcupine_handle.frame_length)
            pcm = struct.unpack_from("h" * porcupine_handle.frame_length, pcm)
            
            keyword_index = porcupine_handle.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                print("Say 'on' or 'off' now...")
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
        """Parse command to extract action - just look for 'on' or 'off'"""
        if not command:
            return None
            
        # Simple check for "on" or "off" anywhere in the command
        command_lower = command.lower().strip()
        
        if "on" in command_lower:
            return "on"
        elif "off" in command_lower:
            return "off"
            
        return None
    
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
        print("Say 'Hey Max' followed by 'on' or 'off'")
        print("Listening...")
        
        try:
            while True:
                # Listen for wake word
                if self.listen_for_wake_word():
                    time.sleep(0.2)  # Brief pause after wake word
                    
                    # Listen for command
                    command = self.listen_for_command()
                    action = self.parse_command(command)
                    
                    if action:
                        # Capture image
                        image = self.capture_image()
                        if image is not None:
                            # Send to server - device will be recognized from image
                            self.send_to_server(image, "visual_target", action)
                        else:
                            print("Failed to capture image")
                    else:
                        print("Could not parse command. Try: 'on' or 'off'")

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage. Don't freeze my laptop :/
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        global audio_stream, pa, porcupine_handle
        
        if audio_stream:
            audio_stream.close()
        if pa:
            pa.terminate()
        if porcupine_handle:
            porcupine_handle.delete()
        if self.camera:
            self.camera.release()

if __name__ == "__main__":
    client = VisualAssistantClient()
    client.run()
