"""
Debug Module - Simple print-based home automation module
This is the default module that just prints commands for testing, since I don't have a Home Assistant server in neighborhood.
"""

def execute_command(device_name, action):
    """
    Execute a command for a device
    
    Args:
        device_name (str): Name of the device
        action (str): Action to perform ("on" or "off")
    
    Returns:
        dict: Result of the command execution
    """
    print(f"DEBUG MODULE: {device_name} -> {action.upper()}")
    
    return {
        "success": True,
        "message": f"Debug: Would turn {device_name} {action}",
        "device": device_name,
        "action": action
    }
