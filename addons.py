import os
import json


# Global addon storage
addons = {}


def load_addons(addons_dir: str):
    """Load all addons from the addons directory."""
    global addons
    addons = {}
    
    if not os.path.exists(addons_dir):
        os.makedirs(addons_dir, exist_ok=True)
        return
    
    for addon_name in os.listdir(addons_dir):
        addon_path = os.path.join(addons_dir, addon_name)
        if not os.path.isdir(addon_path):
            continue
        
        # Look for JSON config
        for filename in os.listdir(addon_path):
            if filename.endswith('.json'):
                json_path = os.path.join(addon_path, filename)
                try:
                    with open(json_path, 'r') as f:
                        config = json.load(f)
                    
                    # Get the Python file
                    py_file = config.get('python', filename.replace('.json', '.py'))
                    py_path = os.path.join(addon_path, py_file)
                    
                    if os.path.exists(py_path):
                        addons[config['tag']] = {
                            'config': config,
                            'python_path': py_path
                        }
                        print(f"Loaded addon: {config['tag']}")
                except Exception as e:
                    print(f"Error loading addon {addon_name}: {e}")


def get_addon(tag: str):
    """Get an addon by its tag name."""
    return addons.get(tag)


def list_addons():
    """List all loaded addons."""
    return list(addons.keys())
