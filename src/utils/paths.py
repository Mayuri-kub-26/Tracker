import os
import sys

def get_app_root():
    """Returns the root directory of the application."""
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Running as a script
        # Assuming this file is in src/utils/paths.py
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_resource_path(relative_path):
    """
    Returns the absolute path to a resource.
    Works for both source and bundled executables.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Only use _MEIPASS if the resource was BUNDLED inside the exe.
        # For things like configs/logs that stay outside, use sys.executable path.
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = get_app_root()

    return os.path.join(base_path, relative_path)

def get_external_path(relative_path):
    """
    Returns a path relative to the executable location.
    Used for files that should stay outside the binary (configs, logs).
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = get_app_root()
        
    return os.path.join(base_path, relative_path)
