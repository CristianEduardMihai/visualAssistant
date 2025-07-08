# VisualAssistant - Smart Home Control System

A modular voice-controlled smart home system that uses computer vision to identify devices and control them through voice commands.

## Features

- Voice activation with wake word detection (Porcupine)
- Computer vision-based device recognition
- Modular architecture (client/server)
- Web UI for device management
- Extensible home automation modules

## Architecture

### Client (Raspberry Pi)
- Camera capture
- Wake word detection
- Speech recognition
- Communication with server

### Server
- Object recognition and classification
- Device management web UI
- Home automation modules
- Image processing

## Setup

### Server Setup
1. Install dependencies: `pip install -r server/requirements.txt`
2. Run the server: `cd server && python3 server.py`
3. Access web UI at: `http://localhost:5000`

### Client Setup
1. Install dependencies: `pip install -r client/requirements.txt`
2. Configure server IP in `client/config.py`
3. Run the client: `cd client && python3 client.py`

## Usage

1. Train the system by uploading device photos through the web UI
2. Say the wake word followed by "turn [device] on/off"
3. The system will capture an image, identify the device, and execute the command