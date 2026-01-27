# Tracking System Technical Documentation

This document explains the core improvements made to the system for deployment on the drone. The changes focus on **Stability**, **Persistence**, and **Accuracy**.

---

## 1. `src/detection/tracker.py` (Core Logic)
This is the most significant update. It now handles advanced tracking scenarios that previously caused the system to fail.

- **NanoTracker Integration**: Replaced basic trackers with a high-performance ONNX-based Nano tracker optimized for real-time edge use.
- **Real-Time Verification**: 
    - Every frame, the system compares the current tracked object against the **Original Template** selected by the user.
    - This prevents "shifting"—where the tracker accidentally jumps to a nearby object or background.
- **Scale-Invariant Tracking**: 
    - Added a resizing algorithm to the verification step.
    - The system now maintains a lock even if the object gets closer or further away (changing size).
- **Smoothed Motion Prediction**: 
    - If the object is obscured (Occluded), the system predicts its path based on smoothed velocity.
    - This allows the box to "follow" the object behind obstacles.
- **Persistence Tuning**: Lowered the confidence threshold to **55%** to handle lighting changes and shadows without losing the lock.

---

## 2. `src/core/app.py` (Main System App)
Updated to integrate the new tracker states into the drone's hardware control loop.

- **Intelligent Status Handling**:
    - The app now understands 3 states: `TRACKING` (Green), `SEARCHING` (Yellow/Predicted), and `LOST` (Red).
- **Gimbal Stability**:
    - During brief overlaps (Searching state), the gimbal is programmed to remain steady or follow the predicted path rather than jerking toward a lost target.
    - Only stops the gimbal if the target is truly `LOST` for more than 2 seconds.
- **Consolidated Imports**: Removed dependencies on the old `track.py` to ensure the drone services use the new optimized logic.

---

## 3. `src/config.yaml` (System Configuration)
Streamlined for production deployment on the drone.

- **Default Tracker**: Set `tracker_type: "NANO"` as the system default.
- **Persistence Settings**:
    - Added configurations for `auto_recover` and `max_recovery_attempts`.
- **RTSP Optimization**: Configured camera and gimbal parameters to be ready for the drone's high-resolution RTSP feed.

---
**Summary**: These changes transform the system from a basic laptop-demo into a professional, robust tracking solution ready for the drone's field operations. faith.
