import os
import sys

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

def check_for_updates():
    """Checks if a newer version exists on GitHub using Web API (No Git required)"""
    import requests
    # Use the Raw GitHub URL to get the VERSION file directly
    REPO_URL = "https://raw.githubusercontent.com/Mayuri-kub-26/Tracker/master/VERSION"
    
    try:
        response = requests.get(REPO_URL, timeout=5)
        if response.status_code == 200:
            remote_version = response.text.strip()
            local_version = get_version()
            
            if remote_version and remote_version != local_version:
                return remote_version
    except Exception as e:
        # Silently fail if no internet
        pass
    return None

def print_version_banner():
    version = get_version()
    print("=" * 40)
    print(f"  TRACKER SYSTEM - VERSION {version}")
    print("=" * 40)

def handle_interactive_update(new_version):
    """Asks user if they want to update and executes it"""
    choice = input(f"\n[!] A new version ({new_version}) is available. Update now? (y/n): ").lower()
    if choice == 'y':
        # Import here to avoid circular dependencies
        try:
            from update_system import update_system
            if update_system():
                print("\n[SUCCESS] System updated. Please restart to finish.")
                sys.exit(0)
        except ImportError:
            print("[ERROR] Update script not found at project root.")
    else:
        print("Continuing with current version...\n")
