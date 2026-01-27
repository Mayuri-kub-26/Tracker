import os
import sys
import subprocess
import requests
import zipfile
import shutil

# Configuration
REPO_OWNER = "Mayuri-kub-26"
REPO_NAME = "Tracker"
ZIP_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/master.zip"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/VERSION"

def run_command(command, cwd=None):
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

import urllib.request

def download_and_extract():
    print(f"Installing {REPO_NAME} for the first time...")
    try:
        urllib.request.urlretrieve(ZIP_URL, "tracker.zip")
        
        with zipfile.ZipFile("tracker.zip", "r") as z:
            z.extractall(".")
        
        # GitHub zips put everything in a subfolder like Tracker-master
        # We find it and rename it to 'Tracker-main'
        extracted_dir = f"{REPO_NAME}-master"
        if os.path.exists(extracted_dir):
            if os.path.exists("Tracker-main"):
                shutil.rmtree("Tracker-main")
            os.rename(extracted_dir, "Tracker-main")
            
        os.remove("tracker.zip")
        print("Installation complete!")
        return True
    except Exception as e:
        print(f"Failed to download: {e}")
        return False

def main():
    print("="*40)
    print(f"    {REPO_NAME} UNIVERSAL LAUNCHER")
    print("="*40)

    project_dir = "Tracker-main"
    
    # 1. Check if project exists
    if not os.path.exists(project_dir):
        if not download_and_extract():
            sys.exit(1)

    # 2. Check for updates
    try:
        print("Checking for updates...")
        with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
            remote_ver = response.read().decode('utf-8').strip()
            
            local_ver_path = os.path.join(project_dir, "VERSION")
            local_ver = "unknown"
            if os.path.exists(local_ver_path):
                with open(local_ver_path, "r") as f:
                    local_ver = f.read().strip()
            
            if remote_ver != local_ver:
                print(f"\n[!] NEW VERSION AVAILABLE: {remote_ver} (You have {local_ver})")
                choice = input("Update now? (y/n): ").lower()
                if choice == 'y':
                    if download_and_extract():
                        print("System updated!")
    except Exception:
        print("No internet or could not check for updates. Running locally...")

    # 3. Launch the app
    print("\nLaunching Tracker...\n")
    main_py = os.path.join(project_dir, "src", "main.py")
    if os.path.exists(main_py):
        # We need to ensure we run it from the project root so imports work
        run_command([sys.executable, "src/main.py", "--mode", "debug"], cwd=project_dir)
    else:
        print(f"Error: Could not find {main_py}")

if __name__ == "__main__":
    main()
