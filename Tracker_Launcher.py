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
CHECK_INTERVAL = 20 

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

def get_git_remote_status(running_hash=None):
    """Checks if there are new commits on the remote branch or if disk version changed."""
    if not is_git_repo(): return False
    try:
        # 1. Fetch current status from remote
        subprocess.run(["git", "fetch"], check=True, capture_output=True)
        
        # 2. Get the latest hashes
        local_hash = get_current_hash()
        remote_hash = subprocess.check_output(["git", "rev-parse", "@{u}"], text=True).strip()
        
        # 3. Same-Machine Detection: If disk code (local_hash) is newer than memory code (running_hash)
        if running_hash and running_hash != "unknown" and running_hash != local_hash:
            # Look inside the new VERSION file on disk
            new_v = get_local_version()
            print(f"[OTA] Local Changes Detected: Memory({running_hash[:7]}) != Disk({local_hash[:7]})")
            return new_v

        # 4. Standard Remote Detection: If local branch is behind remote tracking branch
        if local_hash != remote_hash:
            base = subprocess.check_output(["git", "merge-base", "HEAD", "@{u}"], text=True).strip()
            if base == local_hash:
                print(f"[OTA] Remote Update Detected: Local({local_hash[:7]}) -> Remote({remote_hash[:7]})")
                # We return True which check_for_stable_update handles as "git"
                return True
        return False
    except Exception as e:
        return False

def sync_git():
    """Performs a git pull and returns success."""
    print("[GIT] New changes detected. Syncing code...")
    try:
        subprocess.run(["git", "pull"], check=True)
        print("[GIT] Successfully synced.")
        return True
    except Exception as e:
        print(f"[GIT] Sync failed: {e}")
        return False

def check_for_stable_update(running_hash=None):
    # If we are in a Git repo, check Git status instead of Releases API
    if is_git_repo():
        remote_status = get_git_remote_status(running_hash)
        if remote_status:
            print("[OTA] Mode: Git Sync | Status: Updates Available")
            # remote_status could be True or a Version String
            return ("git" if remote_status is True else remote_status), "git"
        else:
            return None, None

    # Fallback to Binary/ZIP mode for non-git environments
    local_ver = get_local_version()
    print(f"[OTA] Mode: Standalone | Local: v{local_ver}")
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
    # 1. Handle Git Sync
    if download_url == "git":
        return sync_git()

    # 2. Handle ZIP Upgrade (Standalone)
    print(f"[OTA] Starting ZIP upgrade to v{new_version}...")
    temp_zip = "ota_download.zip"
    extract_dir = "ota_extract_temp"
    
    try:
        r = requests.get(download_url, stream=True, timeout=30)
        with open(temp_zip, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        
        if os.path.exists(extract_dir): shutil.rmtree(extract_dir, ignore_errors=True)
        os.makedirs(extract_dir)
        with zipfile.ZipFile(temp_zip, 'r') as z:
            z.extractall(extract_dir)
            
        content_root = None
        for root, dirs, files in os.walk(extract_dir):
            if "VERSION" in files and "_internal" not in root:
                content_root = root
                break
        
        if not content_root:
            print("[ERROR] Could not find application root in ZIP.")
            return False

        ts = int(time.time())
        for root, dirs, files in os.walk(content_root):
            rel_path = os.path.relpath(root, content_root)
            target_dir = "." if rel_path == "." else os.path.join(".", rel_path)
            if not os.path.exists(target_dir): os.makedirs(target_dir, exist_ok=True)
            
            for file in files:
                if file.lower() == os.path.basename(__file__).lower(): continue
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                try:
                    if os.path.exists(dst_file):
                        bak_file = f"{dst_file}.{ts}.old"
                        os.rename(dst_file, bak_file)
                    shutil.move(src_file, dst_file)
                except: pass

        final_ver = get_local_version()
        if version.parse(final_ver) >= version.parse(new_version):
            print(f"[SUCCESS] v{final_ver} confirmed.")
            return True
        return False
    except Exception as e:
        print(f"[CRITICAL] OTA Failed: {e}")
        return False

def main():
    mode = "Git Sync" if is_git_repo() else "Standalone"
    start_version = get_local_version()
    print("="*50)
    print(f"    Tracker PROFESSIONAL LAUNCHER ({mode})")
    print(f"    Current Version: v{start_version}")
    print("="*50)

    # Capture the commit hash we are STARTING with
    running_hash = get_current_hash()
    if running_hash != "unknown":
        print(f"[LAUNCHER] Running Version Hash: {running_hash[:7]}")

    while True:
        # 1. Update Check (before starting)
        v, url = check_for_stable_update(running_hash)
        if v and url:
            new_v_str = f"v{v}" if v != "git" else "latest"
            print(f"\n[OTA] Updating from v{start_version} to {new_v_str}...")
            if perform_upgrade(url, v):
                print("[OTA] Restarting Session...")
                # Re-exec to apply changes
                os.execv(sys.executable, [sys.executable] + sys.argv)

        # 2. Start Application
        print(f"\n[LAUNCHER] Starting {REPO_NAME}...")
        
        should_run_source = is_git_repo()
        exe_path = os.path.join("dist", "TrackerApp", APP_EXE_NAME)
        if not os.path.exists(exe_path):
             exe_path = os.path.join(".", APP_EXE_NAME)

        if should_run_source or not os.path.exists(exe_path):
            print("[LAUNCHER] Running from Source Mode (Developer/Sync active)...")
            app_process = subprocess.Popen([sys.executable, "src/main.py", "--mode", "debug"])
        else:
            print(f"[LAUNCHER] Running from Binary Mode: {exe_path}")
            app_process = subprocess.Popen([exe_path])

        # 3. Monitor
        last_check = time.time()
        while app_process.poll() is None:
            if time.time() - last_check > CHECK_INTERVAL:
                # Pass running_hash to detect if disk version changed
                v, url = check_for_stable_update(running_hash)
                if v and url:
                    new_v_str = f"v{v}" if v != "git" else "latest"
                    print(f"\n[!] HOT RELOAD: Synced changes detected.")
                    print(f"[OTA] Transitioning from v{start_version} to {new_v_str}...")
                    app_process.terminate()
                    app_process.wait()
                    perform_upgrade(url, v)
                    break 
                last_check = time.time()
            time.sleep(1)

        if app_process.poll() == 0:
            print("[LAUNCHER] App closed normally.")
            break
        else:
            print(f"[LAUNCHER] App restarted for update/crash.")
            time.sleep(1)

if __name__ == "__main__":
    main()
