import pyautogui
import cv2
import numpy as np
import time

from src.utils.coords import ScreenTransformer
from src.core.vision import VisionGuard
from src.core.click import safe_click
def main():
    # Initialize your tools
    st = ScreenTransformer()
    guard = VisionGuard()

    # Load your captured 'danger' button template
    danger_template_path = 'assets/danger_btn.png'
    # Note: cv2.imread returns None if image doesn't exist, so check
    forbidden_template = cv2.imread(danger_template_path)
    if forbidden_template is None:
        print(f"❌ Error: Cannot load {danger_template_path}. Please ensure file exists and path is correct.")
        print("Please run this script in the project root directory and ensure assets/danger_btn.png exists.")
        return

    # Get template dimensions and calculate appropriate screenshot area
    template_height, template_width = forbidden_template.shape[:2]
    print(f"📏 Template image dimensions: {template_width}×{template_height} pixels")

    # Calculate required physical pixel area (slightly larger than template, add 20% margin)
    required_physical_width = int(template_width * 1.2)
    required_physical_height = int(template_height * 1.2)

    # Ensure minimum area is 200×200 physical pixels
    required_physical_width = max(required_physical_width, 200)
    required_physical_height = max(required_physical_height, 200)

    print(f"📏 Required screenshot area: {required_physical_width}×{required_physical_height} physical pixels")

    # Get screen dimensions to ensure screenshot area doesn't exceed screen bounds
    screen_width_logical, screen_height_logical = pyautogui.size()
    screen_width_physical, screen_height_physical = st.to_physical(screen_width_logical, screen_height_logical)

    # Check if area is too large
    if required_physical_width > screen_width_physical or required_physical_height > screen_height_physical:
        print(f"⚠️ Warning: Required area exceeds screen dimensions, adjusting to screen size")
        required_physical_width = min(required_physical_width, screen_width_physical)
        required_physical_height = min(required_physical_height, screen_height_physical)

    print(f"📏 Final screenshot area: {required_physical_width}×{required_physical_height} physical pixels")

    # Calculate area size in logical coordinates (for pyautogui)
    required_logic_width = int(required_physical_width / st.scale)
    required_logic_height = int(required_physical_height / st.scale)
    print(f"📏 Logical coordinate area: {required_logic_width}×{required_logic_height} logical points")

    print("🛡️ ClawShield sentinel started, ready for real-time audit of mouse surrounding area...")
    print("Press 'q' key to exit loop.")

    # Enter loop for real-time detection
    while True:
        # 1. Get current mouse logical coordinates
        logic_x, logic_y = pyautogui.position()

        # 2. Convert logical coordinates to physical pixel coordinates (essence of Mac Retina display)
        # We want to capture a physical pixel area centered on the mouse
        physical_center_x, physical_center_y = st.to_physical(logic_x, logic_y)
        
        # Define screenshot area size (physical pixels), dynamically adjusted based on template dimensions
        # Note: pyautogui.screenshot region parameter uses logical coordinates
        # So we need to calculate a corresponding logical area

        # Calculate top-left corner of physical pixel area (centered on mouse)
        half_physical_width = required_physical_width // 2
        half_physical_height = required_physical_height // 2
        physical_region_x = int(physical_center_x - half_physical_width)
        physical_region_y = int(physical_center_y - half_physical_height)

        # Convert top-left corner of physical area to logical coordinates for pyautogui
        logic_region_x, logic_region_y = st.to_logic(physical_region_x, physical_region_y)
        logic_region_width, logic_region_height = required_logic_width, required_logic_height


        # 3. Capture screen area around mouse
        # region parameter: (left, top, width, height) - note these are logical coordinates
        screenshot_pil = pyautogui.screenshot(
            region=(logic_region_x, logic_region_y, logic_region_width, logic_region_height)
        )
        
        # Convert PIL Image to OpenCV format (NumPy array)
        screenshot_cv = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)

        # 4. (Temporary) SIFT feature matching audit
        # Convert both screenshot and template to grayscale because SIFT expects grayscale
        # If your forbidden_template is already loaded in color, need to convert

        # Calculate similarity
        confidence_score = guard.audit_area(screenshot_cv, danger_template_path)

        # Debug: print score (every 10 frames)
        if not hasattr(main, "frame_counter"):
            main.frame_counter = 0
        main.frame_counter += 1
        if main.frame_counter % 10 == 0:
            print(f"🔄 Detection score: {confidence_score:.3f}")

        # 5. Display real-time view and audit results (advanced challenge)
        # Draw mouse point in screenshot (here drawing center point of screenshot)
        cv2.circle(screenshot_cv, (screenshot_cv.shape[1]//2, screenshot_cv.shape[0]//2), 5, (0, 0, 255), -1) # Red dot
        
        # Display confidence score
        cv2.putText(screenshot_cv, f"Risk: {confidence_score:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Pop up a window to display screenshot
        cv2.imshow("ClawShield Live Audit (Press 'q' to quit)", screenshot_cv)
        
        # Wait a bit each loop and detect key press
        if cv2.waitKey(1) & 0xFF == ord('q'): # Press 'q' key to exit
            break
        
        time.sleep(0.05) # Pause slightly to avoid high CPU usage

    cv2.destroyAllWindows() # Close all OpenCV windows on exit
def run_shield_demo():
    print("🎯 Move your mouse to a button and wait 2 seconds...")
    print("ClawShield will scan the area and assess risk automatically")
    import time; time.sleep(2)

    x, y = pyautogui.position()
    print(f"📍 Target coordinates: ({x}, {y})")

    # Use the new safe_click which handles everything internally
    print("🔍 Scanning area for dangerous text...")
    success = safe_click(x, y)

    if success:
        print("✅ Click executed successfully")
    else:
        print("🛑 Click was blocked by user or risk assessment")
if __name__ == "__main__":
    main()