# Client Configuration
SERVER_IP = "192.168.1.100"  # Change this to your server's IP
SERVER_PORT = 5000
API_ENDPOINT = f"http://{SERVER_IP}:{SERVER_PORT}/api/process_command"

# Porcupine wake word settings
PORCUPINE_ACCESS_KEY = "YOUR_PORCUPINE_ACCESS_KEY_HERE"  # Get from https://console.picovoice.ai/
WAKE_WORDS = ["jarvis"]  # Available: alexa, americano, blueberry, bumblebee, computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator
# Could also use a custom wake word, but requires training, no time for it in neighborhood :D

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 512

# Camera settings
CAMERA_INDEX = 0
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
