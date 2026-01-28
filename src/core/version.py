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
    """DEPRECATED: Updates are now handled by Tracker_Launcher.py from GitHub Releases."""
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

def check_and_apply_update():
    """Checks for updates and applies them automatically (used for background updates)"""
    new_version = check_for_updates()
    if new_version:
        print(f"\n" + "!" * 50)
        print(f"  [BACKGROUND UPDATE] New version {new_version} detected!")
        print(f"  System will update from v3 to v4 now...")
        print("!" * 50 + "\n")
        
        try:
            from update_system import update_system
            if update_system():
                print("\n[SUCCESS] Update applied successfully.")
                print("[INFO] Restarting application to apply Version 4 features...\n")
                
                # Restart logic for Windows/Linux
                import subprocess
                python = sys.executable
                args = [python] + sys.argv
                
                if os.name == 'nt':
                    # On Windows, start a new process and exit the current one
                    subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    sys.exit(0)
                else:
                    # On Unix, replace the current process
                    os.execv(python, args)
                    
        except Exception as e:
            print(f"[ERROR] Background update failed: {e}")
            return False
    return True
