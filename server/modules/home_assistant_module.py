"""
Home Assistant Module - Integration with Home Assistant
Uncomment and configure this module to use with Home Assistant
"""

import requests

HOME_ASSISTANT_URL = "http://192.168.1.50:8123"
HOME_ASSISTANT_TOKEN = "your_long_lived_access_token_here"

def execute_command(device_name, action):
    """
    Execute a command via Home Assistant API
    
    Args:
        device_name (str): Name of the device (entity_id in HA)
        action (str): Action to perform ("on" or "off")

    Returns:
        dict: Result of the command execution
    """ 
    # Uncomment and configure for actual Home Assistant integration
    try:
        headers = {
            "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Map action to Home Assistant service
        service = "turn_on" if action == "on" else "turn_off"
        
        url = f"{HOME_ASSISTANT_URL}/api/services/homeassistant/{service}"
        data = {"entity_id": device_name}
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Successfully turned {device_name} {action}",
                "device": device_name,
                "action": action
            }
        else:
            return {
                "success": False,
                "message": f"Failed to control {device_name}: {response.text}",
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
    