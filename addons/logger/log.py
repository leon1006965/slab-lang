"""Logger addon for Slab."""

import os
from datetime import datetime


def run(attributes):
    """Execute the log action."""
    file_path = attributes.get('file', '')
    message = attributes.get('message', '')
    
    if not file_path:
        return "Error: No file specified"
    
    if not message:
        return "Error: No message specified"
    
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format log entry
        log_entry = f"[{timestamp}] {message}\n"
        
        # Append to file
        with open(file_path, 'a') as f:
            f.write(log_entry)
        
        return f"Logged to {file_path}: {message}"
    
    except Exception as e:
        return f"Error logging: {e}"
