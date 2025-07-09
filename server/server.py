from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory
import cv2
import numpy as np
from PIL import Image
import io
import importlib
import os
import config
from device_recognition import DeviceRecognizer

app = Flask(__name__)
app.secret_key = "ironman_helmet_secret_key_change_this"

# Initialize device recognizer
recognizer = DeviceRecognizer()

def load_automation_module():
    """Load the configured home automation module"""
    try:
        module = importlib.import_module(f"modules.{config.DEFAULT_MODULE}")
        return module
    except ImportError as e:
        print(f"Error loading module {config.DEFAULT_MODULE}: {e}")
        # Fallback to debug module
        return importlib.import_module("modules.debug_module")

automation_module = load_automation_module()

@app.route('/')
def index():
    """Main web interface"""
    devices = recognizer.get_devices_list()
    return render_template('index.html', devices=devices)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    """Add a new device with training images"""
    if request.method == 'POST':
        device_name = request.form.get('device_name')
        images = request.files.getlist('device_images')
        
        if not device_name:
            flash('Device name is required', 'error')
            return redirect(url_for('add_device'))
        
        if len(images) < 1:
            flash('At least one image is required', 'error')
            return redirect(url_for('add_device'))
        
        # Convert to PIL Images
        pil_images = []
        for img_file in images:
            if img_file.filename != '':
                try:
                    pil_img = Image.open(img_file.stream)
                    pil_images.append(pil_img)
                except Exception as e:
                    flash(f'Error processing image {img_file.filename}: {e}', 'error')
                    return redirect(url_for('add_device'))
        
        if len(pil_images) == 0:
            flash('No valid images uploaded', 'error')
            return redirect(url_for('add_device'))
        
        # Add device
        try:
            recognizer.add_device(device_name, pil_images)
            flash(f'Device "{device_name}" added successfully with {len(pil_images)} images', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding device: {e}', 'error')
            return redirect(url_for('add_device'))
    
    return render_template('add_device.html')

@app.route('/delete_device/<device_name>', methods=['POST'])
def delete_device(device_name):
    """Delete a device"""
    if recognizer.delete_device(device_name):
        flash(f'Device "{device_name}" deleted successfully', 'success')
    else:
        flash(f'Error deleting device "{device_name}"', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/process_command', methods=['POST'])
def process_command():
    """API endpoint to process commands from client"""
    try:
        # Get image and command data
        image_file = request.files.get('image')
        device_query = request.form.get('device', '').strip()
        action = request.form.get('action', '').strip()
        
        if not image_file or not device_query or not action:
            return jsonify({
                "success": False,
                "message": "Missing image, device, or action"
            }), 400
        
        # Process image
        image_data = image_file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({
                "success": False,
                "message": "Invalid image data"
            }), 400
        
        # Recognize device
        recognized_device, confidence = recognizer.recognize_device(image)
        
        if recognized_device is None:
            return jsonify({
                "success": False,
                "message": f"Could not recognize any device in image. Confidence: {confidence:.2f}"
            }), 404
        
        # For visual_target, we use whatever device is recognized
        # For specific device names, we validate the recognition matches
        if device_query == "visual_target":
            target_device = recognized_device
        else:
            # Check if recognized device matches the requested device (fuzzy matching)
            if device_query.lower() not in recognized_device.lower() and recognized_device.lower() not in device_query.lower():
                return jsonify({
                    "success": False,
                    "message": f"Recognized '{recognized_device}' but requested '{device_query}'. Confidence: {confidence:.2f}"
                }), 400
            target_device = recognized_device
        
        # Execute command via automation module
        result = automation_module.execute_command(target_device, action)
        
        # Add recognition info to result
        result["recognized_device"] = recognized_device
        result["target_device"] = target_device
        result["confidence"] = confidence
        result["requested_device"] = device_query
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/device_images/<device_name>/<filename>')
def device_images(device_name, filename):
    """Serve device images"""
    device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
    return send_from_directory(device_dir, filename)

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """API endpoint to get list of devices"""
    devices = recognizer.get_devices_list()
    return jsonify({"devices": devices})

@app.route('/edit_device/<device_name>')
def edit_device(device_name):
    """Edit device page"""
    device_details = recognizer.get_device_details(device_name)
    if not device_details:
        flash(f'Device "{device_name}" not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit_device.html', device=device_details)

@app.route('/update_device_name/<device_name>', methods=['POST'])
def update_device_name(device_name):
    """Update device name"""
    new_name = request.form.get('new_name', '').strip()
    
    if not new_name:
        flash('Device name cannot be empty', 'error')
        return redirect(url_for('edit_device', device_name=device_name))
    
    if recognizer.update_device_name(device_name, new_name):
        flash(f'Device renamed to "{new_name}"', 'success')
        return redirect(url_for('edit_device', device_name=new_name))
    else:
        flash(f'Failed to rename device. Name "{new_name}" may already exist.', 'error')
        return redirect(url_for('edit_device', device_name=device_name))

@app.route('/delete_device_image/<device_name>/<image_filename>', methods=['POST'])
def delete_device_image(device_name, image_filename):
    """Delete a specific image from a device"""
    if recognizer.delete_device_image(device_name, image_filename):
        flash(f'Image "{image_filename}" deleted', 'success')
    else:
        flash(f'Failed to delete image "{image_filename}"', 'error')
    
    return redirect(url_for('edit_device', device_name=device_name))

@app.route('/add_device_images/<device_name>', methods=['POST'])
def add_device_images(device_name):
    """Add new images to an existing device"""
    images = request.files.getlist('new_images')
    
    if len(images) < 1:
        flash('No images selected', 'error')
        return redirect(url_for('edit_device', device_name=device_name))
    
    # Convert to PIL Images
    pil_images = []
    for img_file in images:
        if img_file.filename != '':
            try:
                pil_img = Image.open(img_file.stream)
                pil_images.append(pil_img)
            except Exception as e:
                flash(f'Error processing image {img_file.filename}: {e}', 'error')
                return redirect(url_for('edit_device', device_name=device_name))
    
    if len(pil_images) == 0:
        flash('No valid images uploaded', 'error')
        return redirect(url_for('edit_device', device_name=device_name))
    
    # Add images
    if recognizer.add_device_images(device_name, pil_images):
        flash(f'Added {len(pil_images)} new images to "{device_name}"', 'success')
    else:
        flash('Failed to add images', 'error')
    
    return redirect(url_for('edit_device', device_name=device_name))

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(config.DEVICE_PHOTOS_DIR, exist_ok=True)
    
    print("VisualAssistant Server Starting...")
    print(f"Web UI will be available at: http://localhost:{config.PORT}")
    print(f"Home automation module: {config.DEFAULT_MODULE}")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
