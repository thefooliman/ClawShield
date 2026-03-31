import hashlib
import json
import os
from typing import List, Tuple, Optional

class RiskEngine:
    """
    Multi-factor risk assessment engine
    Factors:
    1. Keyword matching (50%)
    2. Position/context (25%)
    3. History/repetition (10%)
    4. LLM visual analysis (15%)
    """

    def __init__(self):
        # Dangerous words with weights
        self.dangerous_words = {
            "delete": 1.0,
            "confirm": 0.9,
            "subscribe": 0.8,
            "payment": 1.0,
            "install": 0.7,
            "download": 0.6,
            "pay": 1.0,
            "remove": 0.9,
            "uninstall": 0.8,
            "cancel": 0.7,
            "submit": 0.6,
            "agree": 0.6,
            "accept": 0.6,
            "purchase": 0.9,
            "buy": 0.9,
            "transfer": 0.8,
        }

        # Center position risk - clicks near screen center might be more dangerous
        self.center_risk_factor = 0.25  # Reduced from 0.3 to accommodate LLM factor

        # LLM visual analysis
        self.llm_factor = 0.15  # LLM contributes up to 15% of total risk
        self.use_llm = True  # Enable/disable LLM analysis
        self.ollama_classifier = None

        # Try to import Ollama integration
        try:
            from .ollama_integration import get_ollama_classifier
            self.ollama_classifier = get_ollama_classifier()
            if not self.ollama_classifier.is_available():
                print("⚠️ Ollama not available, LLM analysis disabled")
                self.use_llm = False
            else:
                print("✅ Ollama integration available")
        except ImportError:
            print("⚠️ Ollama integration not available")
            self.use_llm = False

        # Load historical data if exists
        self.history_file = "clawshield_history.json"
        self.history = self._load_history()

    def _load_history(self):
        """Load historical click data"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_history(self):
        """Save historical click data"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except:
            pass

    def _calculate_position_risk(self, x: int, y: int) -> float:
        """
        Calculate risk based on screen position
        Clicks near center (likely UI buttons) are higher risk
        """
        import pyautogui
        screen_width, screen_height = pyautogui.size()

        # Normalize coordinates
        norm_x = abs(x - screen_width / 2) / (screen_width / 2)
        norm_y = abs(y - screen_height / 2) / (screen_height / 2)

        # Distance from center (0 at center, 1 at edge)
        distance = (norm_x**2 + norm_y**2)**0.5

        # Risk is higher when closer to center (lower distance)
        position_risk = 1.0 - distance

        # Scale by center risk factor
        return max(0.0, position_risk) * self.center_risk_factor

    def _calculate_word_risk(self, text: str) -> Tuple[float, List[str]]:
        """
        Calculate risk based on dangerous words in text
        Returns: (risk_score, matched_words)
        """
        text_lower = text.lower()
        matched_words = []
        total_weight = 0.0

        for word, weight in self.dangerous_words.items():
            if word in text_lower:
                matched_words.append(word)
                total_weight += weight

        # Normalize to max of 1.0 (can exceed 1 if multiple high-risk words)
        max_possible = sum(sorted([w for w in self.dangerous_words.values()], reverse=True)[:3])
        word_risk = min(1.0, total_weight / max_possible) if max_possible > 0 else 0.0

        # Apply word risk factor (50%)
        return word_risk * 0.5, matched_words

    def _calculate_history_risk(self, text_hash: str, x: int, y: int) -> float:
        """
        Calculate risk based on previous interactions
        If this exact action has been allowed before, lower risk
        """
        key = f"{text_hash}_{x}_{y}"

        if key in self.history:
            allowed_count = self.history[key].get("allowed", 0)
            blocked_count = self.history[key].get("blocked", 0)
            total = allowed_count + blocked_count

            if total > 0:
                # If allowed more than blocked, lower risk
                if allowed_count > blocked_count:
                    # Trust factor: 0.1 max reduction
                    trust_factor = min(0.1, allowed_count * 0.02)
                    return -trust_factor  # Negative means risk reduction

                # If blocked more than allowed, increase risk
                elif blocked_count > allowed_count:
                    suspicion_factor = min(0.05, blocked_count * 0.01)
                    return suspicion_factor

        return 0.0

    def _calculate_llm_risk(self, image, text: str) -> Tuple[float, str]:
        """
        Calculate risk based on LLM visual analysis
        Returns: (risk_score, reason)
        """
        if not self.use_llm or self.ollama_classifier is None:
            return 0.0, ""

        try:
            # Only use LLM for moderate-risk cases to save time
            # This check happens in calculate() method
            llm_risk = self.ollama_classifier.analyze_risk(image, text)

            # Apply LLM factor (15% of total risk)
            weighted_llm_risk = llm_risk * self.llm_factor

            reason = ""
            if llm_risk > 0.7:
                reason = "LLM: High visual deception risk"
            elif llm_risk > 0.3:
                reason = "LLM: Moderate visual deception risk"
            elif llm_risk > 0:
                reason = "LLM: Low visual deception risk"

            return weighted_llm_risk, reason
        except Exception as e:
            print(f"⚠️ LLM risk calculation error: {e}")
            return 0.0, ""

    def calculate(self, text: str, x: int, y: int, image=None) -> Tuple[float, List[str]]:
        """
        Calculate overall risk score for a potential click
        Args:
            text: Extracted text from the UI element
            x, y: Click coordinates
            image: Optional screenshot for visual analysis
        Returns: (risk_score, reasons)
        """
        # Calculate word-based risk
        word_risk, matched_words = self._calculate_word_risk(text)

        # Calculate position risk
        position_risk = self._calculate_position_risk(x, y)

        # Calculate history risk (hash text for consistency)
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        history_risk = self._calculate_history_risk(text_hash, x, y)

        # Combine base risks
        total_risk = word_risk + position_risk + history_risk

        # Calculate LLM visual risk if image is provided and risk is moderate
        llm_risk = 0.0
        llm_reason = ""
        if image is not None and self.use_llm:
            # Only use LLM for moderate-risk cases (0.2-0.8) to save time
            if 0.2 <= total_risk <= 0.8:
                llm_risk, llm_reason = self._calculate_llm_risk(image, text)
            else:
                print(f"📊 Skipping LLM analysis (base risk: {total_risk:.2f})")

        # Add LLM risk
        total_risk += llm_risk

        # Clamp to [0, 1]
        total_risk = max(0.0, min(1.0, total_risk))

        # Build reasons
        reasons = []
        if matched_words:
            reasons.append(f"Dangerous words: {', '.join(matched_words)}")
        if position_risk > 0.1:
            reasons.append("Center-screen position")
        if history_risk < 0:
            reasons.append("Previously allowed")
        elif history_risk > 0:
            reasons.append("Previously blocked")
        if llm_reason:
            reasons.append(llm_reason)

        return total_risk, reasons

    def record_action(self, text: str, x: int, y: int, allowed: bool):
        """
        Record the outcome of an action for future risk assessment
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        key = f"{text_hash}_{x}_{y}"

        if key not in self.history:
            self.history[key] = {"allowed": 0, "blocked": 0}

        if allowed:
            self.history[key]["allowed"] += 1
        else:
            self.history[key]["blocked"] += 1

        self._save_history()

    def is_trusted(self, text: str, x: int, y: int, threshold: int = 3) -> bool:
        """
        Check if an action should be trusted based on history
        Returns True if allowed >= threshold and allowed > blocked
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        key = f"{text_hash}_{x}_{y}"

        if key in self.history:
            allowed = self.history[key].get("allowed", 0)
            blocked = self.history[key].get("blocked", 0)

            if allowed >= threshold and allowed > blocked:
                return True

        return False