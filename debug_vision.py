#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
from src.core.vision import VisionGuard

def test_vision():
    print("=== Testing VisionGuard ===")

    # 1. Create test object
    guard = VisionGuard()
    print("✅ VisionGuard initialized successfully")

    # 2. Check template image
    template_path = 'assets/danger_btn.png'
    if not os.path.exists(template_path):
        print(f"❌ Template image does not exist: {template_path}")
        return

    print(f"✅ Template image exists: {template_path}")

    # 3. Read template image
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ Cannot read template image: {template_path}")
        return

    print(f"✅ Template image read successfully, dimensions: {template.shape}")

    # 4. Test template feature point detection
    kp1, des1 = guard.sift.detectAndCompute(template, None)
    print(f"Template feature points count: {len(kp1)}")
    print(f"Template descriptor: {'Exists' if des1 is not None else 'None'}")
    if des1 is not None:
        print(f"Descriptor shape: {des1.shape}")

    # 5. Create a simple test screenshot (solid color)
    test_screenshot = np.zeros((200, 200, 3), dtype=np.uint8)
    test_screenshot[:] = (100, 100, 100)  # Gray

    # 6. Detailed analysis of matching process
    print("\n=== Detailed matching analysis ===")

    # Copy audit_area logic but add debug information
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    gray_screenshot = cv2.cvtColor(test_screenshot, cv2.COLOR_BGR2GRAY)

    kp1, des1 = guard.sift.detectAndCompute(template, None)
    kp2, des2 = guard.sift.detectAndCompute(gray_screenshot, None)

    print(f"Template feature points (kp1): {len(kp1)}")
    print(f"Screenshot feature points (kp2): {len(kp2)}")
    print(f"Template descriptor: {'Exists' if des1 is not None else 'None'}")
    print(f"Screenshot descriptor: {'Exists' if des2 is not None else 'None'}")

    if des1 is None or des2 is None or len(kp1) == 0:
        print("❌ Insufficient feature points, directly returning 0.0")
        score = 0.0
    else:
        print(f"Descriptor shapes: des1={des1.shape if des1 is not None else None}, des2={des2.shape if des2 is not None else None}")

        # KNN matching
        matches = guard.flann.knnMatch(des1, des2, k=2)
        print(f"Raw match pairs count: {len(matches)}")

        # Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)

        print(f"Good matches count: {len(good_matches)}")
        score = len(good_matches) / len(kp1)
        print(f"Calculated score: {len(good_matches)} / {len(kp1)} = {score}")

    # Also call original function
    original_score = guard.audit_area(test_screenshot, template_path)
    print(f"✅ audit_area returned score: {original_score}")

    # 7. Test real screenshot (simulating main program logic)
    try:
        import pyautogui
        from src.utils.coords import ScreenTransformer

        st = ScreenTransformer()
        print(f"\n=== Simulating main program screenshot ===")
        print(f"Screen scaling factor: {st.scale}")

        # Get mouse position
        logic_x, logic_y = pyautogui.position()
        print(f"Mouse logical coordinates: ({logic_x}, {logic_y})")

        # Convert to physical coordinates
        physical_center_x, physical_center_y = st.to_physical(logic_x, logic_y)
        print(f"Mouse physical coordinates: ({physical_center_x}, {physical_center_y})")

        # Calculate screenshot area (same as main program)
        physical_region_x = int(physical_center_x - 100)
        physical_region_y = int(physical_center_y - 100)
        logic_region_x, logic_region_y = st.to_logic(physical_region_x, physical_region_y)
        logic_region_width, logic_region_height = int(200 / st.scale), int(200 / st.scale)

        print(f"Logical screenshot area: ({logic_region_x}, {logic_region_y}, {logic_region_width}, {logic_region_height})")

        # Capture screen
        screenshot_pil = pyautogui.screenshot(
            region=(logic_region_x, logic_region_y, logic_region_width, logic_region_height)
        )
        screenshot_cv = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
        print(f"✅ Captured mouse surrounding area, dimensions: {screenshot_cv.shape}")

        # Save screenshot for inspection
        cv2.imwrite('debug_screenshot.png', screenshot_cv)
        print("✅ Screenshot saved as debug_screenshot.png")

        # Analyze screenshot feature points
        gray_screenshot = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        kp2, des2 = guard.sift.detectAndCompute(gray_screenshot, None)
        print(f"Mouse area screenshot feature points count: {len(kp2)}")
        print(f"Mouse area screenshot descriptor: {'Exists' if des2 is not None else 'None'}")

        # Call audit_area
        real_score = guard.audit_area(screenshot_cv, template_path)
        print(f"✅ Real screenshot matching score: {real_score}")

        # If score is 0, try template matching for comparison
        if real_score == 0.0:
            print("\n=== Trying template matching for comparison ===")
            # Convert template to color for template matching
            template_color = cv2.imread(template_path)
            if template_color is not None:
                # Adjust template dimensions to fit screenshot area (if needed)
                if template_color.shape[0] > screenshot_cv.shape[0] or template_color.shape[1] > screenshot_cv.shape[1]:
                    print(f"Template dimensions {template_color.shape} larger than screenshot dimensions {screenshot_cv.shape}, need adjustment")
                    # Can adjust, but skip for now
                else:
                    result = cv2.matchTemplate(screenshot_cv, template_color, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    print(f"Template matching max similarity: {max_val:.3f}")
                    if max_val > 0.5:
                        print(f"Possible match location: {max_loc}")

    except Exception as e:
        print(f"⚠️ 无法截取真实屏幕: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vision()