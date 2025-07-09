import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
from PIL import Image
import config

class DeviceRecognizer:
    def __init__(self):
        self.devices_db_path = config.DEVICES_DATABASE
        self.devices = self.load_devices()
        
    def load_devices(self):
        """Load devices database"""
        if os.path.exists(self.devices_db_path):
            with open(self.devices_db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_devices(self):
        """Save devices database"""
        with open(self.devices_db_path, 'w') as f:
            json.dump(self.devices, f, indent=2)
    
    def extract_features(self, image):
        """Extract simple features from image using OpenCV"""
        if isinstance(image, str):
            image = cv2.imread(image)
        
        # Resize image
        image = cv2.resize(image, config.TARGET_IMAGE_SIZE)
        
        # Convert to different color spaces and extract features
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate histograms
        hist_gray = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        
        # Normalize histograms
        hist_gray = cv2.normalize(hist_gray, hist_gray).flatten()
        hist_h = cv2.normalize(hist_h, hist_h).flatten()
        hist_s = cv2.normalize(hist_s, hist_s).flatten()
        
        # Combine features
        features = np.concatenate([hist_gray, hist_h, hist_s])
        
        return features
    
    def add_device(self, device_name, image_files):
        """Add a new device with training images"""
        device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
        os.makedirs(device_dir, exist_ok=True)
        
        features_list = []
        
        for i, image_file in enumerate(image_files):
            # Save image
            image_path = os.path.join(device_dir, f"image_{i}.jpg")
            image_file.save(image_path)
            
            # Extract features
            image = cv2.imread(image_path)
            features = self.extract_features(image)
            features_list.append(features.tolist())
        
        # Store device info
        self.devices[device_name] = {
            "name": device_name,
            "features": features_list,
            "image_count": len(image_files)
        }
        
        self.save_devices()
        return True
    
    def recognize_device(self, image):
        """Recognize device in the given image"""
        if len(self.devices) == 0:
            return None, 0
        
        # Extract features from input image
        input_features = self.extract_features(image)
        
        best_match = None
        best_similarity = 0
        
        # Compare with all devices
        for device_name, device_data in self.devices.items():
            device_features = device_data["features"]
            
            # Calculate similarity with each training image
            similarities = []
            for features in device_features:
                similarity = cosine_similarity([input_features], [features])[0][0]
                similarities.append(similarity)
            
            # Use the maximum similarity
            max_similarity = max(similarities)
            
            if max_similarity > best_similarity:
                best_similarity = max_similarity
                best_match = device_name
        
        # Return result if above threshold
        if best_similarity >= config.SIMILARITY_THRESHOLD:
            return best_match, best_similarity
        else:
            return None, best_similarity
    
    def get_devices_list(self):
        """Get list of all registered devices"""
        return [{"name": name, "image_count": data["image_count"]} 
                for name, data in self.devices.items()]
    
    def delete_device(self, device_name):
        """Delete a device and its images"""
        if device_name in self.devices:
            # Remove from database
            del self.devices[device_name]
            self.save_devices()
            
            # Remove image directory
            device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
            if os.path.exists(device_dir):
                import shutil
                shutil.rmtree(device_dir)
            
            return True
        return False
    
    def get_device_details(self, device_name):
        """Get detailed information about a specific device"""
        if device_name not in self.devices:
            return None
        
        device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
        image_files = []
        
        if os.path.exists(device_dir):
            for filename in os.listdir(device_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    image_files.append(filename)
        
        return {
            "name": device_name,
            "image_count": self.devices[device_name]["image_count"],
            "images": sorted(image_files)
        }
    
    def update_device_name(self, old_name, new_name):
        """Update device name"""
        if old_name not in self.devices:
            return False
        
        if new_name != old_name and new_name in self.devices:
            return False  # New name already exists
        
        # Update database
        self.devices[new_name] = self.devices[old_name]
        self.devices[new_name]["name"] = new_name
        del self.devices[old_name]
        
        # Rename directory
        old_dir = os.path.join(config.DEVICE_PHOTOS_DIR, old_name)
        new_dir = os.path.join(config.DEVICE_PHOTOS_DIR, new_name)
        
        if os.path.exists(old_dir):
            os.rename(old_dir, new_dir)
        
        self.save_devices()
        return True
    
    def delete_device_image(self, device_name, image_filename):
        """Delete a specific image from a device"""
        if device_name not in self.devices:
            return False
        
        device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
        image_path = os.path.join(device_dir, image_filename)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
            # Recalculate features for remaining images
            self._recalculate_device_features(device_name)
            return True
        
        return False
    
    def add_device_images(self, device_name, image_files):
        """Add new images to an existing device"""
        if device_name not in self.devices:
            return False
        
        device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
        os.makedirs(device_dir, exist_ok=True)
        
        # Find next available image number
        existing_files = [f for f in os.listdir(device_dir) if f.startswith('image_')]
        next_num = len(existing_files)
        
        features_list = self.devices[device_name]["features"]
        
        for i, image_file in enumerate(image_files):
            # Save image
            image_path = os.path.join(device_dir, f"image_{next_num + i}.jpg")
            image_file.save(image_path)
            
            # Extract features
            image = cv2.imread(image_path)
            features = self.extract_features(image)
            features_list.append(features.tolist())
        
        # Update device info
        self.devices[device_name]["features"] = features_list
        self.devices[device_name]["image_count"] = len(features_list)
        
        self.save_devices()
        return True
    
    def _recalculate_device_features(self, device_name):
        """Recalculate features for all images of a device"""
        device_dir = os.path.join(config.DEVICE_PHOTOS_DIR, device_name)
        features_list = []
        
        if os.path.exists(device_dir):
            image_files = [f for f in os.listdir(device_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            
            for image_file in image_files:
                image_path = os.path.join(device_dir, image_file)
                image = cv2.imread(image_path)
                if image is not None:
                    features = self.extract_features(image)
                    features_list.append(features.tolist())
        
        # Update device info
        self.devices[device_name]["features"] = features_list
        self.devices[device_name]["image_count"] = len(features_list)
        self.save_devices()
