import cv2
import sys
import os

# Add src to path so we can import ObjectTracker
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.detection.tracker import ObjectTracker
    from src.core.config import cfg
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Ensure you are running this from the project root.")
    sys.exit(1)

# State for mouse selection
selection_start = None
selection_end = None
selecting = False
new_roi = None

def on_mouse(event, x, y, flags, param):
    global selection_start, selection_end, selecting, new_roi
    
    if event == cv2.EVENT_LBUTTONDOWN:
        selection_start = (x, y)
        selecting = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            selection_end = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        selection_end = (x, y)
        selecting = False
        # Calculate ROI: x, y, w, h
        x1, y1 = selection_start
        x2, y2 = selection_end
        ix = min(x1, x2)
        iy = min(y1, y2)
        iw = abs(x1 - x2)
        ih = abs(y1 - y2)
        if iw > 5 and ih > 5:
            new_roi = (ix, iy, iw, ih)

def run_webcam_test():
    global new_roi, selection_start, selection_end, selecting
    
    # Force NANO tracker for this test
    os.environ["TRACKER_TYPE"] = "NANO"
    
    print("Initializing Webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    tracker = ObjectTracker()
    tracking_active = False

    window_name = "NanoTracker Live Interactive Selection"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse)

    print("\n--- LIVE INTERACTIVE MODE ---")
    print("1. Click and DRAG your mouse to select any object.")
    print("2. Release to start tracking - video stays live!")
    print("3. Press 'R' to RE-SELECT (Reset tracking).")
    print("4. Press 'C' to clear tracking.")
    print("5. Press 'Q' to quit.")
    print("------------------------------\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        display_frame = frame.copy()

        # Handle new selection from mouse callback
        if new_roi is not None:
            tracker.init(frame, new_roi)
            tracking_active = True
            new_roi = None
            selection_start = None
            selection_end = None

        # Helper for professional overlay
        def draw_status(img, status_text, color):
            # Status bar background
            cv2.rectangle(img, (0, 0), (img.shape[1], 45), (30, 30, 30), -1)
            # Status dot
            cv2.circle(img, (25, 23), 8, color, -1)
            # Status text
            cv2.putText(img, status_text, (50, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            # Instructions on bottom
            cv2.rectangle(img, (0, img.shape[0]-35), (img.shape[1], img.shape[0]), (30, 30, 30), -1)
            cv2.putText(img, "R: Re-select | C: Clear | Q: Quit", (20, img.shape[0]-12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        if tracking_active:
            success, bbox = tracker.update(frame)
            
            # Use the tracker's internal status for feedback
            confidence_pct = int(tracker.current_confidence * 100)
            
            if success:
                x, y, w, h = [int(v) for v in bbox]
                # Draw main tracking box with corners
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                length = 20
                cv2.line(display_frame, (x, y), (x+length, y), (0, 255, 0), 3)
                cv2.line(display_frame, (x, y), (x, y+length), (0, 255, 0), 3)
                cv2.line(display_frame, (x+w, y), (x+w-length, y), (0, 255, 0), 3)
                cv2.line(display_frame, (x+w, y), (x+w, y+length), (0, 255, 0), 3)
                
                draw_status(display_frame, f"STATUS: TRACKING ({confidence_pct}%)", (0, 255, 0))
            else:
                # Handle Searching/Lost state visualization
                if tracker.status == "LOST":
                    draw_status(display_frame, "STATUS: TARGET LOST", (0, 0, 255))
                else:
                    draw_status(display_frame, f"STATUS: SEARCHING / OCCLUDED ({confidence_pct}%)", (0, 255, 255))
                
                # Show where we think the object is if we have a last valid bbox
                if tracker.last_valid_bbox is not None:
                    x, y, w, h = [int(v) for v in tracker.last_valid_bbox]
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (255, 0, 255), 1)
                    cv2.putText(display_frame, "Predicted Position", (x, y-5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
        
        # Draw current selection box while dragging
        if selecting and selection_start and selection_end:
            cv2.rectangle(display_frame, selection_start, selection_end, (255, 255, 0), 2)
            draw_status(display_frame, "STATUS: SELECTING TARGET...", (255, 255, 0))
        elif not tracking_active:
            draw_status(display_frame, "STATUS: IDLE - Drag Mouse to Track", (200, 200, 200))

        cv2.imshow(window_name, display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c') or key == ord('r'):
            tracker.stop()
            tracking_active = False
            new_roi = None
            selection_start = None
            selection_end = None
            if key == ord('r'):
                print("Re-select mode: Click and drag to select new object.")
            else:
                print("Tracking cleared.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Check if models exist
    if not os.path.exists("models/nanotrack_backbone.onnx") or \
       not os.path.exists("models/nanotrack_head.onnx"):
        print("Error: NanoTrack models not found in models/ directory.")
        print("Please run 'python download_models.py' first.")
    else:
        run_webcam_test()
