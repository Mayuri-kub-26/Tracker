import os

def get_version():
    """Reads version from VERSION file at project root"""
    try:
        # Move up two levels from src/core/version.py to reach root
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        version_path = os.path.join(root, "VERSION")
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return "unknown"

def print_version_banner():
    version = get_version()
    print("=" * 40)
    print(f"  TRACKER SYSTEM - VERSION {version}")
    print("=" * 40)
