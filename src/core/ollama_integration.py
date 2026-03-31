import requests
import base64
import json
import time
from typing import Optional, Tuple
from PIL import Image
import io
import os

class OllamaVisionClassifier:
    """
    Local LLM vision classifier using Ollama
    Analyzes UI screenshots to detect deceptive buttons
    """

    def __init__(self,
                 model: str = "llava",
                 ollama_host: str = "http://localhost:11434",
                 timeout: int = 30):
        """
        Initialize Ollama vision classifier

        Args:
            model: Ollama model name (default: "llava" for vision)
            ollama_host: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.ollama_host = ollama_host.rstrip('/')
        self.timeout = timeout
        self.available = self._check_ollama_available()

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _image_to_base64(self, image) -> str:
        """
        Convert image to base64 string
        Supports PIL Image, numpy array, or file path
        """
        if isinstance(image, str):  # File path
            with open(image, "rb") as f:
                img_bytes = f.read()
        elif hasattr(image, 'save'):  # PIL Image
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
        elif hasattr(image, 'tobytes'):  # numpy array
            # Assume it's an OpenCV image (BGR)
            import cv2
            # Convert BGR to RGB for better compatibility
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.png', image)
            img_bytes = buffer.tobytes()
        else:
            raise ValueError("Unsupported image format")

        return base64.b64encode(img_bytes).decode('utf-8')

    def classify_ui_element(self, image, context: str = "") -> Tuple[bool, float, str]:
        """
        Classify a UI element as deceptive or safe

        Args:
            image: Image to analyze (PIL, numpy, or file path)
            context: Optional textual context from OCR

        Returns:
            (is_deceptive, confidence, reasoning)
            is_deceptive: True if button looks deceptive
            confidence: Confidence score (0-1)
            reasoning: Model's reasoning text
        """
        if not self.available:
            print("⚠️ Ollama not available, skipping visual analysis")
            return False, 0.0, "Ollama not available"

        try:
            # Prepare the prompt
            prompt = """You are a UI safety classifier.

Analyze this UI element (button, link, or interface component).

Does this element look like:
1. An advertisement disguised as content?
2. A forced subscription or misleading opt-in?
3. A deceptive download button (fake "Download" or "Install")?
4. A phishing attempt or security risk?

Answer format:
YES or NO - then briefly explain why.

Context from text recognition: {context}
""".format(context=context if context else "No text detected")

            # Convert image to base64
            image_base64 = self._image_to_base64(image)

            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent YES/NO
                    "num_predict": 100,   # Limit response length
                }
            }

            # Send request to Ollama
            start_time = time.time()
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            elapsed = time.time() - start_time

            if response.status_code != 200:
                print(f"⚠️ Ollama API error: {response.status_code}")
                return False, 0.0, f"API error: {response.status_code}"

            result = response.json()
            response_text = result.get("response", "").strip()
            print(f"🤖 Ollama response ({elapsed:.1f}s): {response_text[:100]}...")

            # Parse YES/NO from response
            is_deceptive, confidence, reasoning = self._parse_response(response_text)
            return is_deceptive, confidence, reasoning

        except Exception as e:
            print(f"⚠️ Ollama classification error: {e}")
            return False, 0.0, f"Error: {str(e)}"

    def _parse_response(self, response_text: str) -> Tuple[bool, float, str]:
        """
        Parse model response to extract YES/NO and confidence

        Returns:
            (is_deceptive, confidence, reasoning)
        """
        response_lower = response_text.lower()
        reasoning = response_text.strip()

        # Check for YES/NO patterns
        if response_lower.startswith("yes") or "yes," in response_lower:
            is_deceptive = True
            # Try to extract confidence from response
            confidence = self._extract_confidence(response_lower)
            return is_deceptive, confidence, reasoning

        elif response_lower.startswith("no") or "no," in response_lower:
            is_deceptive = False
            confidence = self._extract_confidence(response_lower)
            return is_deceptive, confidence, reasoning

        # If not clear, check for keywords
        deceptive_keywords = [
            "deceptive", "misleading", "advertisement", "ad", "fake",
            "phishing", "scam", "dangerous", "risky", "untrustworthy"
        ]
        safe_keywords = [
            "safe", "legitimate", "genuine", "trustworthy", "normal",
            "standard", "expected", "appropriate"
        ]

        deceptive_count = sum(1 for word in deceptive_keywords if word in response_lower)
        safe_count = sum(1 for word in safe_keywords if word in response_lower)

        if deceptive_count > safe_count:
            is_deceptive = True
            confidence = 0.6  # Moderate confidence
        elif safe_count > deceptive_count:
            is_deceptive = False
            confidence = 0.6
        else:
            # Ambiguous response
            is_deceptive = False
            confidence = 0.3
            reasoning = "Ambiguous response: " + reasoning

        return is_deceptive, confidence, reasoning

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from text"""
        # Look for percentage or confidence indicators
        import re

        # Check for percentages like "80%" or "80 percent"
        percent_pattern = r'(\d{1,3})%'
        match = re.search(percent_pattern, text)
        if match:
            return float(match.group(1)) / 100.0

        # Check for fractional confidence like "0.8" or ".8"
        decimal_pattern = r'\b(0?\.\d+|\d\.\d+)\b'
        matches = re.findall(decimal_pattern, text)
        if matches:
            try:
                return max(0.0, min(1.0, float(matches[0])))
            except:
                pass

        # Check for verbal confidence indicators
        if "highly confident" in text or "very confident" in text:
            return 0.9
        elif "confident" in text:
            return 0.7
        elif "somewhat" in text or "moderately" in text:
            return 0.5
        elif "unsure" in text or "uncertain" in text:
            return 0.3

        # Default confidence
        return 0.7

    def analyze_risk(self, image, context: str = "") -> float:
        """
        Simplified interface: returns risk score (0-1)
        where 1.0 is highest risk

        This is the main method to be called by risk_engine
        """
        is_deceptive, confidence, _ = self.classify_ui_element(image, context)

        if is_deceptive:
            # Deceptive button: risk = confidence (0-1)
            return confidence
        else:
            # Safe button: risk = 0
            return 0.0

    def is_available(self) -> bool:
        """Check if Ollama is available"""
        return self.available


# Singleton instance for easy access
_ollama_classifier = None

def get_ollama_classifier() -> OllamaVisionClassifier:
    """Get or create singleton Ollama classifier"""
    global _ollama_classifier
    if _ollama_classifier is None:
        _ollama_classifier = OllamaVisionClassifier()
    return _ollama_classifier

def analyze_ui_risk(image, context: str = "") -> float:
    """
    Convenience function for risk analysis
    Returns risk score (0-1) based on visual classification
    """
    classifier = get_ollama_classifier()
    return classifier.analyze_risk(image, context)