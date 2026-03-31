import os
import pyautogui
from .risk_engine import RiskEngine
from .history_store import HistoryStore
from .vision import VisionGuard

# Initialize components as singletons
_risk_engine = None
_history_store = None
_vision = None

def _get_components():
    """Lazy initialization of components"""
    global _risk_engine, _history_store, _vision
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    if _history_store is None:
        _history_store = HistoryStore()
    if _vision is None:
        _vision = VisionGuard()
    return _risk_engine, _history_store, _vision

def safe_click(x, y):
    """
    Enhanced Safe Click: Automated audit entry point
    Performs visual audit, risk assessment, and history checking
    Returns: True if click was executed, False if blocked
    """
    risk_engine, history_store, vision = _get_components()

    # 1. Automatic environment sampling
    screenshot = vision.capture_around(x, y)
    text = vision.extract_text(screenshot)

    if not text:
        text = ""  # Empty text if OCR fails

    print(f"🔍 Scanned text: '{text}' at ({x}, {y})")

    # 2. Check historical trust records
    if history_store.is_trusted(text, x, y):
        print(f"✨ Trusted action: '{text}'. Clicking...")
        pyautogui.click(x, y)
        return True

    # 3. Comprehensive risk scoring (now includes LLM visual analysis)
    risk_score, reasons = risk_engine.calculate(text, x, y, screenshot)

    print(f"📊 Risk score: {risk_score:.2f}")
    if reasons:
        print(f"📝 Reasons: {', '.join(reasons)}")

    # 4. Dynamic threshold judgment
    if risk_score > 0.7:  # High risk threshold
        msg = f"⚠️ High Risk ({risk_score:.2f}): {', '.join(reasons) if reasons else 'Potential danger detected'}"

        # Use macOS native dialog
        cmd = f'display dialog "{msg}. Proceed?" buttons {{"Block", "Allow"}} default button "Block" with icon caution'
        response = os.popen(f"osascript -e '{cmd}'").read()

        if "Allow" in response:
            # User allowed - record action for future trust
            history_store.record_action(text, x, y, allowed=True)
            risk_engine.record_action(text, x, y, allowed=True)
            pyautogui.click(x, y)
            print(f"✅ User allowed high-risk click at ({x}, {y})")
            return True
        else:
            # User blocked
            history_store.record_action(text, x, y, allowed=False)
            risk_engine.record_action(text, x, y, allowed=False)
            print(f"🛑 Shield Active: User blocked click at ({x}, {y})")
            return False

    elif risk_score > 0.3:  # Medium risk - warn but auto-proceed
        print(f"⚠️ Medium risk ({risk_score:.2f}), proceeding with caution")
        pyautogui.click(x, y)
        # Record as allowed for future reference
        history_store.record_action(text, x, y, allowed=True)
        risk_engine.record_action(text, x, y, allowed=True)
        return True

    # Low risk - direct pass
    pyautogui.click(x, y)
    return True

# Backward compatibility wrapper
def safe_click_legacy(x, y, risk_score, found_words=None):
    """
    Legacy version for compatibility with existing code
    Converts old API to new implementation
    """
    print("⚠️ Using legacy safe_click interface - consider upgrading")

    # If high risk, use old dialog logic
    if risk_score > 0.5:
        msg = f"Detected sensitive words: {', '.join(found_words) if found_words else 'Unknown risk'}"
        cmd = f'display dialog "{msg}. Do you want to proceed?" buttons {{"Cancel", "Confirm"}} default button "Cancel" with icon caution'
        response = os.popen(f"osascript -e '{cmd}'").read()

        if "Confirm" not in response:
            print("🛑 Click intercepted by user.")
            return False

    pyautogui.click(x, y)
    print(f"✅ Safe click executed at ({x}, {y})")
    return True