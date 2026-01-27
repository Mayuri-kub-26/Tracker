# Git Completion Checklist: Nano Tracker Integration

Follow these steps to commit the perfectly optimized tracker to your repository.

## 1. Core Logic Changes
- [ ] `src/detection/tracker.py`: Main tracking logic with NanoTracker, Occlusion Handling, and Stability fixes.
- [ ] `src/detection/bytetracker/matching.py`: Windows IoU fallback implementation.
- [ ] `src/detection/hailo_inference.py` & `src/detection/__init__.py`: Robust fallbacks for laptop/PC dev without Hailo hardware.

## 2. Configuration & Assets
- [ ] `src/config.yaml`: Set `tracker_type: "NANO"` and configure your RTSP URL.
- [ ] `models/`: Ensure `nanotrack_backbone.onnx` and `nanotrack_head.onnx` are present.
    - *Note: Don't commit large model files to Git unless using Git LFS.*

## 3. Deployment & Testing
- [ ] `download_models.py`: Use this script to fetch required ONNX models.
- [ ] `test_webcam.py`: The reference UI for live testing with mouse-selection and status indicators.

## 4. Final Cleanup
- [x] All debug `print` statements replaced with `logging`.
- [x] Placeholder/experimental code removed.
- [x] No hardcoded camera IDs; uses `config.yaml` RTSP settings.

---
**Ready for Commit!**
`git add src/detection/track.py src/detection/bytetracker/matching.py test_webcam.py src/config.yaml`
`git commit -m "feat: integrate high-performance NanoTracker with occlusion handling and RTSP support"`
