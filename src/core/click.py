import os
import pyautogui

def safe_click(x, y, risk_score, found_words=None):
    if risk_score > 0.5:
        msg = f"Detected sensitive words: {', '.join(found_words)}"
        cmd = f'display dialog "{msg}. Do you want to proceed?" buttons {{"Cancel", "Confirm"}} default button "Cancel" with icon caution'
        response = os.popen(f"osascript -e '{cmd}'").read()
        
        if "Confirm" not in response:
            print("🛑 Click intercepted by user.")
            return False

    pyautogui.click(x, y)
    print(f"✅ Safe click executed at ({x}, {y})")
    return True