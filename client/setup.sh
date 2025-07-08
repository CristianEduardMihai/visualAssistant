#!/bin/bash

# Iron Man Helmet - Client Setup Script

echo "Iron Man Helmet Client Setup"
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Install system dependencies for audio
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "Client setup complete!"
echo ""
echo "IMPORTANT: Configure your settings in config.py:"
echo "   - Set SERVER_IP to your server's IP address"
echo "   - Get a Porcupine access key from https://console.picovoice.ai/"
echo "   - Set PORCUPINE_ACCESS_KEY in config.py"
echo ""
echo "To run the client:"
echo "   cd client"
echo "   source venv/bin/activate"
echo "   python3 client.py"
