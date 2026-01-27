qimport subprocess
import os
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e.stderr}")
        return None

def update_system():
    print("Checking for updates via Git (OTA)...")
    
    # Ensure we are on the right branch
    branch = run_command("git rev-parse --abbrev-ref HEAD")
    if not branch:
        print("Error: Could not determine current branch.")
        return

    print(f"Current branch: {branch}")
    
    # Perform git pull
    print("Fetching latest changes from origin...")
    output = run_command(f"git pull origin {branch}")
    
    if output:
        print(f"Git Output: {output}")
        if "Already up to date." in output:
            print("System is already at the latest version.")
        else:
            # Re-read version after pull
            version = "unknown"
            if os.path.exists("VERSION"):
                with open("VERSION", "r") as f:
                    version = f.read().strip()
            print(f"\n[OTA] Update Successful! New Version: {version}")
            print("Please restart the application to apply changes.")
            return True
    else:
        print("OTA Update failed. Check your internet connection and Git remote settings.")
        return False

if __name__ == "__main__":
    update_system()
