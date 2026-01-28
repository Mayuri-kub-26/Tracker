import subprocess
import os
import sys
import shutil

def build():
    print("="*50)
    print("   TRACKER BINARY BUILD SYSTEM")
    print("="*50)

    # 1. Clean previous builds
    print("\n[1/4] Cleaning old build files...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  - Removed {folder}/")

    # 2. Run PyInstaller
    print("\n[2/4] Running PyInstaller...")
    try:
        subprocess.run(['pyinstaller', '--noconfirm', 'tracker.spec'], check=True)
        print("\n[SUCCESS] PyInstaller finished.")
    except Exception as e:
        print(f"\n[ERROR] PyInstaller failed: {e}")
        return

    # 3. Verify output
    dist_path = os.path.join('dist', 'TrackerApp')
    exe_path = os.path.join(dist_path, 'TrackerApp.exe' if os.name == 'nt' else 'TrackerApp')
    
    if os.path.exists(exe_path):
        print(f"\n[3/4] Binary located at: {exe_path}")
    else:
        print("\n[ERROR] Output binary not found!")
        return

    # 4. ZIP for Distribution
    print("\n[4/4] Creating distribution ZIP...")
    zip_name = "Tracker_Windows_v3" if os.name == 'nt' else "Tracker_Linux_v3"
    shutil.make_archive(zip_name, 'zip', dist_path)
    print(f"\n[DONE] Release package created: {zip_name}.zip")
    print("\nUpload this ZIP to your GitHub Release as an asset.")

if __name__ == "__main__":
    # Check for PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found! Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    build()
