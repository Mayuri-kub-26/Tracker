import os
import sys
import subprocess
import time
import requests
import zipfile
import shutil
from packaging import version # Requires: pip install packaging

# --- CONFIGURATION ---
REPO_OWNER = "Mayuri-kub-26"
REPO_NAME = "Tracker"
RELEASE_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
APP_EXE_NAME = "TrackerApp.exe" if os.name == 'nt' else "TrackerApp"
CHECK_INTERVAL = 30 
HEALTH_CHECK_TIMEOUT = 30 # Seconds to wait for app to be "healthy"
MAX_CRASH_RETRIES = 3    # Number of times to retry before rollback

def check_internet():
    """Checks if internet is available by pinging GitHub API."""
    try:
        requests.get("https://api.github.com", timeout=5)
        return True
    except:
        return False

def get_local_version():
    """Reads the version file from the root or src directory."""
    for p in ["VERSION", "src/VERSION"]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    v = f.read().strip().lower().replace('v', '')
                    if v: return v
            except: pass
    return "unknown"

def is_git_repo():
    """Checks if the current folder is a Git repository."""
    return os.path.exists(".git")

def get_current_hash():
    """Gets the hash of the current local HEAD."""
    if not is_git_repo(): return "unknown"
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except:
        return "unknown"

def rollback_git(stable_hash):
    """Rolls back to a specific stable hash."""
    if not is_git_repo() or not stable_hash or stable_hash == "unknown":
        print("[ROLLBACK] No stable hash available for rollback.")
        return False
    
    print(f"[ROLLBACK] Reverting to stable hash: {stable_hash[:7]}...")
    try:
        subprocess.run(["git", "reset", "--hard", stable_hash], check=True)
        print("[ROLLBACK] Successfully reverted.")
        return True
    except Exception as e:
        print(f"[ROLLBACK] Failed to revert: {e}")
        return False

def get_git_remote_status(running_hash=None):
    """Checks if there are new commits on the remote branch or if disk version changed."""
    if not is_git_repo(): return False
    if not check_internet():
        print("[OTA] Offline: Skipping update check.")
        return False

    try:
        # 1. Fetch current status from remote
        subprocess.run(["git", "fetch"], check=True, capture_output=True)
        
        # 2. Get the latest hashes
        local_hash = get_current_hash()
        remote_hash = subprocess.check_output(["git", "rev-parse", "@{u}"], text=True).strip()
        
        # 3. Same-Machine Detection: If disk code (local_hash) is newer than memory code (running_hash)
        if running_hash and running_hash != "unknown" and running_hash != local_hash:
            new_v = get_local_version()
            print(f"[OTA] Local Changes Detected: Memory({running_hash[:7]}) != Disk({local_hash[:7]})")
            return new_v

        # 4. Standard Remote Detection: If local branch is behind remote tracking branch
        if local_hash != remote_hash:
            base = subprocess.check_output(["git", "merge-base", "HEAD", "@{u}"], text=True).strip()
            if base == local_hash:
                print(f"[OTA] Remote Update Detected: Local({local_hash[:7]}) -> Remote({remote_hash[:7]})")
                return True
        return False
    except Exception as e:
        return False

def sync_git():
    """Performs a git pull and returns success."""
    if not check_internet(): return False
    print("[GIT] New changes detected. Syncing code...")
    try:
        subprocess.run(["git", "pull"], check=True)
        print("[GIT] Successfully synced.")
        return True
    except Exception as e:
        print(f"[GIT] Sync failed: {e}")
        return False

def check_for_stable_update(running_hash=None):
    if is_git_repo():
        remote_status = get_git_remote_status(running_hash)
        if remote_status:
            return ("git" if remote_status is True else remote_status), "git"
        else:
            return None, None

    # Fallback to Binary/ZIP mode (Static Releases)
    if not check_internet(): return None, None
    local_ver = get_local_version()
    try:
        response = requests.get(RELEASE_API_URL, headers={'Cache-Control': 'no-cache'}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            remote_tag = data['tag_name'].lower().replace('v', '')
            if version.parse(remote_tag) > version.parse(local_ver):
                for asset in data['assets']:
                    if asset['name'].lower().endswith('.zip'):
                        return remote_tag, asset['browser_download_url']
    except: pass
    return None, None

def perform_upgrade(download_url, new_version):
    if download_url == "git":
        return sync_git()
    
    # Standalone ZIP upgrade (if needed)
    print(f"[OTA] Starting ZIP upgrade to v{new_version}...")
    # ... (skipping long zip logic for brevity as user uses git on Pi)
    return False

def main():
    mode = "Git Sync" if is_git_repo() else "Standalone"
    start_version = get_local_version()
    print("="*50)
    print(f"    Tracker ROBUST LAUNCHER ({mode})")
    print(f"    Current Version: v{start_version}")
    print("="*50)

    # Checkpoint: Save the initial hash as "stable"
    stable_hash = get_current_hash()
    running_hash = stable_hash
    crash_count = 0

    while True:
        # 1. Update Check (before starting)
        v, url = check_for_stable_update(running_hash)
        if v and url:
            new_v_str = f"v{v}" if v != "git" else "latest"
            print(f"\n[OTA] Updating from v{start_version} to {new_v_str}...")
            # Checkpoint before upgrade
            pre_upgrade_hash = get_current_hash()
            
            if perform_upgrade(url, v):
                print("[OTA] Restarting Session...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("[ERROR] Update failed. Staying on current version.")

        # 2. Start Application
        print(f"\n[LAUNCHER] Starting {REPO_NAME}...")
        
        exe_path = os.path.join(".", APP_EXE_NAME)
        if is_git_repo() or not os.path.exists(exe_path):
            app_process = subprocess.Popen([sys.executable, "src/main.py"])
        else:
            app_process = subprocess.Popen([exe_path])

        # 3. Monitor
        start_time = time.time()
        last_check = time.time()
        
        while app_process.poll() is None:
            # 3a. Update Check during run
            if time.time() - last_check > CHECK_INTERVAL:
                v, url = check_for_stable_update(running_hash)
                if v and url:
                    print(f"\n[!] HOT RELOAD: Synced changes detected.")
                    app_process.terminate()
                    app_process.wait()
                    perform_upgrade(url, v)
                    # Successful sync: checkpoint this as the NEW stable hash
                    stable_hash = get_current_hash()
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                last_check = time.time()
            time.sleep(1)

        # 4. Handle Exit/Crash
        exit_code = app_process.poll()
        if exit_code == 0:
            print("[LAUNCHER] App closed normally.")
            break
        else:
            runtime = time.time() - start_time
            print(f"[LAUNCHER] App crashed/stopped with code {exit_code} after {runtime:.1f}s")
            
            if runtime < HEALTH_CHECK_TIMEOUT:
                crash_count += 1
                print(f"[LAUNCHER] Critical failure detected ({crash_count}/{MAX_CRASH_RETRIES}).")
                
                if crash_count >= MAX_CRASH_RETRIES:
                    print("[FATAL] Multiple failures. Triggering ROLLBACK...")
                    if rollback_git(stable_hash):
                        crash_count = 0 # Reset after rollback
                        print("[ROLLBACK] Restarting stable version...")
                    else:
                        print("[CRITICAL] Rollback failed or unavailable.")
                        break
            else:
                # App ran long enough to be considered "healthy" at some point
                crash_count = 0 
            
            time.sleep(2)

if __name__ == "__main__":
    main()
