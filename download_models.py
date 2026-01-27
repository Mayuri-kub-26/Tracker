import urllib.request
import os

def download_file(url, path):
    print(f"Downloading {url} to {path}...")
    try:
        # User-Agent header to avoid some blocks
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, path)
        # Check if it's HTML (common error)
        with open(path, 'rb') as f:
            head = f.read(100)
            if b'<!DOCTYPE html>' in head or b'<html' in head:
                print(f"Error: Downloaded file {path} appears to be HTML, not a binary model.")
                # Print the first few lines to see what it is
                with open(path, 'r', errors='ignore') as f2:
                    print(f2.read(500))
                return False
        print(f"Downloaded {path} successfully.")
        return True
    except Exception as e:
        print(f"Failed to download {url}. Error: {e}")
        return False

models_dir = "models"
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

# Correct raw URLs from HonglinChu repository
backbone_url = "https://github.com/HonglinChu/SiamTrackers/raw/refs/heads/master/NanoTrack/models/nanotrackv2/nanotrack_backbone_sim.onnx"
head_url = "https://github.com/HonglinChu/SiamTrackers/raw/refs/heads/master/NanoTrack/models/nanotrackv2/nanotrack_head_sim.onnx"

download_file(backbone_url, os.path.join(models_dir, "nanotrack_backbone.onnx"))
download_file(head_url, os.path.join(models_dir, "nanotrack_head.onnx"))
