"""File Encrypter addon for Slab."""

import os
import base64


def run(attributes):
    """Execute the encrypt action."""
    file_path = attributes.get('file', '')
    password = attributes.get('password', '')
    
    if not file_path:
        return "Error: No file specified"
    
    if not password:
        return "Error: No password specified"
    
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"
    
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Simple XOR encryption (for demo - use real encryption in production)
        password_bytes = password.encode()
        encrypted = bytearray()
        for i, byte in enumerate(content):
            encrypted.append(byte ^ password_bytes[i % len(password_bytes)])
        
        # Save encrypted file
        encrypted_path = file_path + '.encrypted'
        with open(encrypted_path, 'wb') as f:
            f.write(bytes(encrypted))
        
        return f"Encrypted: {file_path} -> {encrypted_path}"
    
    except Exception as e:
        return f"Error encrypting file: {e}"
