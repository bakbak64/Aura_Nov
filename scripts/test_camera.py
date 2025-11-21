import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import load_config
from core.camera import Camera


def test_camera():
    print("=== AURA Camera Test ===")
    print()
    
    config = load_config()
    camera = Camera(config)
    
    print("Attempting to start camera...")
    if not camera.start():
        print("ERROR: Could not start camera!")
        print("Possible issues:")
        print("1. Camera is being used by another application")
        print("2. Camera is not connected")
        print("3. Wrong device ID in config.yaml")
        return False
    
    print("Camera started successfully!")
    print("Press 'q' to quit, or wait 10 seconds...")
    
    import time
    start_time = time.time()
    
    while time.time() - start_time < 10:
        frame = camera.get_raw_frame()
        if frame is not None:
            cv2.imshow('Camera Test', frame)
            print(f"Frame captured: {frame.shape}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.stop()
    cv2.destroyAllWindows()
    
    print()
    print("Camera test complete!")
    return True


if __name__ == "__main__":
    test_camera()

