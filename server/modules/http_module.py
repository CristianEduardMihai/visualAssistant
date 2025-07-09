"""
Generic HTTP Module - Control devices via HTTP requests
This module can be used for custom smart home setups that accept HTTP commands
"""

import requests
import json

# Configuration - edit these for your setup
DEVICE_ENDPOINTS = {
    # Example configuration:
    # "tv": {
    #     "on": "http://192.168.1.50/tv/on",
    #     "off": "http://192.168.1.50/tv/off"
    # },
    # "lights": {
    #     "on": "http://192.168.1.51/lights/on", 
    #     "off": "http://192.168.1.51/lights/off"
    # }
}

# Default timeout for HTTP requests
REQUEST_TIMEOUT = 5

def execute_command(device_name, action):
    """
    Execute a command via HTTP request
    
    Args:
        device_name (str): Name of the device
        action (str): Action to perform ("on" or "off")
    
    Returns:
        dict: Result of the command execution
    """
    
    # Check if device is configured
    device_lower = device_name.lower()
    if device_lower not in DEVICE_ENDPOINTS:
        return {
            "success": False,
            "message": f"Device '{device_name}' not configured in HTTP module",
            "device": device_name,
            "action": action
        }
    
    # Check if action is supported
    if action not in DEVICE_ENDPOINTS[device_lower]:
        return {
            "success": False,
            "message": f"Action '{action}' not configured for device '{device_name}'",
            "device": device_name,
            "action": action
        }
    
    # Get the endpoint URL
    url = DEVICE_ENDPOINTS[device_lower][action]
    
    try:
        # Make HTTP request
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Successfully turned {device_name} {action}",
                "device": device_name,
                "action": action,
                "http_status": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"HTTP request failed with status {response.status_code}",
                "device": device_name,
                "action": action,
                "http_status": response.status_code
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": f"Request to {device_name} timed out",
            "device": device_name,
            "action": action
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": f"Could not connect to {device_name}",
            "device": device_name,
            "action": action
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error controlling {device_name}: {str(e)}",
            "device": device_name,
            "action": action
        }
