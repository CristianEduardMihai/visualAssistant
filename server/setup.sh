#!/bin/bash

# VisualAssistant - Server Setup Script

echo "VisualAssistant Server Setup"
echo "============================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install APT packages
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip
#sudo apt-get install python3-distutils


# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "Server setup complete!"
echo ""
echo "To run the server:"
echo "   cd server"
echo "   source .venv/bin/activate"
echo "   python3 server.py"
echo ""
echo "The web UI will be available at: http://localhost:5000"
