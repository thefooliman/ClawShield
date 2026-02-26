import cv2
import numpy as np
import pytesseract
class VisionGuard:
    def __init__(self):
        # Initialize SIFT algorithm for detecting image feature points
        self.sift = cv2.SIFT_create()
        # Use FLANN matcher, faster than brute-force matching
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

    def template_match(self, screenshot_cv, template_path):
        """
        Calculate similarity using template matching (as fallback for SIFT matching)
        """
        # Read color template
        template = cv2.imread(template_path)
        if template is None:
            return 0.0

        # If template is larger than screenshot, resize template
        if template.shape[0] > screenshot_cv.shape[0] or template.shape[1] > screenshot_cv.shape[1]:
            # Calculate scaling ratio
            scale = min(screenshot_cv.shape[0] / template.shape[0], screenshot_cv.shape[1] / template.shape[1])
            new_width = int(template.shape[1] * scale * 0.9)  # Slightly shrink to ensure full visibility
            new_height = int(template.shape[0] * scale * 0.9)
            template = cv2.resize(template, (new_width, new_height))

        # Perform template matching
        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return float(max_val)

    def audit_area(self, screenshot_cv, template_path):
        """
        Compare similarity between current screenshot and template image
        """
        # Read template and convert to grayscale
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            return 0.0

        # Convert real-time screenshot to grayscale
        gray_screenshot = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

        # Find feature points and descriptors
        kp1, des1 = self.sift.detectAndCompute(template, None)
        kp2, des2 = self.sift.detectAndCompute(gray_screenshot, None)

        # Calculate SIFT matching score (if possible)
        sift_score = 0.0
        if des1 is not None and des2 is not None and len(kp1) > 0 and des2.shape[0] >= 2:
            # KNN matching
            matches = self.flann.knnMatch(des1, des2, k=2)

            # Lowe's ratio test: filter out noise
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)

            # Calculate score: successful matches / total template feature points
            sift_score = len(good_matches) / len(kp1)

        # Calculate template matching score (as fallback)
        template_score = self.template_match(screenshot_cv, template_path)

        # Return the highest score from both matching methods
        return max(sift_score, template_score)
def get_text_from_region(image_np):
    """
    Convert screenshot to grayscale and recognize text
    """
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    # OCR optimization for small images: binarization
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, lang='eng')
    return text.lower().strip()