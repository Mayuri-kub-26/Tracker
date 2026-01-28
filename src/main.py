import argparse
import sys
import os

from pathlib import Path

def read_version():
    try:
        return Path("VERSION").read_text().strip()
    except:
        return "unknown"

print("=================================")
print("Running Tracker Version:", read_version())
print("This is the new version v6.2.0")
print("=================================")


# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import cfg
from src.core.app import TrackingApp
from src.core.version import print_version_banner, check_for_updates, handle_interactive_update

def main():
    print_version_banner()
    
    # Updates are now handled by Tracker_Launcher.py
        
    from src.core.version import get_version
    print(f"\n>>> Running Tracker System: Version {get_version()} <<<")
    print(">>> [V6 FEATURE] Real-time System Health Telemetry Active <<<\n")
    parser = argparse.ArgumentParser(description="SIYI/Hailo Tracking System")
    parser.add_argument("--mode", default="debug", choices=["debug", "production"], help="Operation mode")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    args = parser.parse_args()

    # Override config with args
    if args.headless:
        cfg._config['system']['headless'] = True
    elif args.mode == 'debug' and not os.environ.get('DISPLAY'):
        print("[INFO] No DISPLAY variable set. Assuming attached monitor at :0")
        os.environ["DISPLAY"] = ":0"
    
    cfg._config['system']['mode'] = args.mode

    if args.mode == 'production':
        print("[INFO] Starting in Production Mode (API Server)")
        from src.api.server import run_server
        # run_server blocks
        run_server(host=cfg.get("api.host"), port=cfg.get("api.port"))
    else:
        app = TrackingApp(mode=args.mode)
        app.start()

if __name__ == "__main__":
    main()
