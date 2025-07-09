# Server Configuration
import os

HOST = "0.0.0.0"
PORT = 5000
# Set DEBUG=False in environment variable for production
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']

# Device photos storage
DEVICE_PHOTOS_DIR = "device_photos"
DEVICES_DATABASE = "devices.json"

# Image processing settings
TARGET_IMAGE_SIZE = (224, 224)
SIMILARITY_THRESHOLD = 0.7  # Adjust based on testing

# Home automation module settings
DEFAULT_MODULE = "debug_module"  # Change to your preferred module
