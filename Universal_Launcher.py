import os
import sys
import subprocess
import time
import urllib.request
import zipfile
import shutil
import threading

# Configuration
REPO_OWNER = "Mayuri-kub-26"
REPO_NAME = "Tracker"
ZIP_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/master.zip"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/VERSION"

# Polling Interval (seconds)
CHECK_INTERVAL = 10 

def run_command(command, cwd=None):
    try:
        if isinstance(command, list):
            subprocess.run(command, check=True, cwd=cwd)
        else:
            subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def download_and_extract(project_dir):
    print(f"[LAUNCHER] Downloading {REPO_NAME} update...")
    try:
        urllib.request.urlretrieve(ZIP_URL, "tracker.zip")
        
        with zipfile.ZipFile("tracker.zip", "r") as z:
            z.extractall(".")
        
        extracted_dir = f"{REPO_NAME}-master"
        if os.path.exists(extracted_dir):
            # Move files from extracted_dir to project_dir
            for item in os.listdir(extracted_dir):
                s = os.path.join(extracted_dir, item)
                d = os.path.join(project_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            shutil.rmtree(extracted_dir)
            
        os.remove("tracker.zip")
        print("[LAUNCHER] Update extracted successfully!")
        return True
    except Exception as e:
        print(f"[LAUNCHER] Failed to download: {e}")
        return False

def update_via_git(project_dir):
    print("[LAUNCHER] Updating via Git Pull...")
    try:
        # Check if it's actually a git repo
        if os.path.exists(os.path.join(project_dir, ".git")):
            subprocess.run("git pull", shell=True, check=True, cwd=project_dir)
            return True
        else:
            print("[LAUNCHER] Not a Git repository, falling back to ZIP download.")
            return download_and_extract(project_dir)
    except Exception as e:
        print(f"[LAUNCHER] Git update failed: {e}. Falling back to ZIP.")
        return download_and_extract(project_dir)

def check_for_updates(project_dir):
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
            remote_ver = response.read().decode('utf-8').strip()
            
            local_ver_path = os.path.join(project_dir, "VERSION")
            local_ver = "unknown"
            if os.path.exists(local_ver_path):
                with open(local_ver_path, "r") as f:
                    local_ver = f.read().strip()
            
            if remote_ver != local_ver and remote_ver != "":
                return remote_ver
    except Exception:
        pass
    return None

def main():
    print("="*50)
    print(f"    {REPO_NAME} AUTO-UPDATING UNIVERSAL LAUNCHER")
    print("    Running in Hot-Reload Mode")
    print("="*50)

    # Use current directory as project root if Universal_Launcher.py is inside it
    if os.path.exists("src/main.py"):
        project_dir = "."
    elif os.path.exists("Tracker-main/src/main.py"):
        project_dir = "Tracker-main"
    else:
        print("[ERROR] Could not find Tracker source. Downloading...")
        project_dir = "Tracker-main"
        if not download_and_extract(project_dir):
            sys.exit(1)

    while True:
        print(f"\n[LAUNCHER] Starting {REPO_NAME}...")
        main_py = os.path.join(project_dir, "src", "main.py")
        
        # Start the app as a subprocess
        # We use sys.executable to ensure we use the same Python environment
        app_process = subprocess.Popen(
            [sys.executable, main_py, "--mode", "debug"],
            cwd=project_dir
        )
        
        print(f"[LAUNCHER] Main app PID: {app_process.pid}")
        print(f"[LAUNCHER] Monitoring for updates every {CHECK_INTERVAL}s...\n")
        
        update_found = False
        new_version = None
        
        # Monitor the process and check for updates
        while app_process.poll() is None:
            new_version = check_for_updates(project_dir)
            if new_version:
                print(f"\n[!] UPDATE DETECTED: {new_version}")
                update_found = True
                break
            time.sleep(CHECK_INTERVAL)
            
        if update_found:
            print("[LAUNCHER] Terminating current version for update...")
            app_process.terminate()
            try:
                app_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("[LAUNCHER] Force killing app...")
                app_process.kill()
            
            # Perform update
            if update_via_git(project_dir):
                print(f"[LAUNCHER] Successfully updated to {new_version}!")
                print("[LAUNCHER] Restarting in 3 seconds...")
                time.sleep(3)
                continue # Restart loop
            else:
                print("[LAUNCHER] Update failed. Retrying app start...")
                continue
        
        # If the app exited on its own
        ret_code = app_process.poll()
        if ret_code is not None:
            if ret_code == 0:
                print("\n[LAUNCHER] App exited normally.")
                break
            else:
                print(f"\n[LAUNCHER] App crashed with exit code {ret_code}. Restarting in 5s...")
                time.sleep(5)

if __name__ == "__main__":
    main()
