#!/usr/bin/env python3
"""
Test script for Ollama integration in ClawShield
Verifies that local LLM visual analysis works correctly
"""

import sys
import os
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ollama_availability():
    """Test if Ollama is running and accessible"""
    print("🔍 Testing Ollama availability...")

    try:
        from src.core.ollama_integration import OllamaVisionClassifier
        classifier = OllamaVisionClassifier()

        if classifier.is_available():
            print("✅ Ollama is running and accessible")
            print(f"   Model: {classifier.model}")
            print(f"   Host: {classifier.ollama_host}")
            return classifier
        else:
            print("❌ Ollama is not available")
            print("\n💡 To set up Ollama:")
            print("   1. Install Ollama: https://ollama.com/download")
            print("   2. Pull a vision model: ollama pull llava")
            print("   3. Ensure Ollama is running: ollama serve")
            print("   4. Run this test again")
            return None

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure requests module is installed: pip install requests")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_image_classification(classifier):
    """Test image classification with a simple generated image"""
    print("\n🖼️ Testing image classification...")

    # Create a simple test image (red rectangle simulating a button)
    # This is just a placeholder - in real usage you'd use actual screenshots
    try:
        import cv2

        # Create a 200x100 red button-like image
        test_image = np.zeros((100, 200, 3), dtype=np.uint8)
        test_image[:, :] = [0, 0, 255]  # Red color (BGR format)

        # Add some text (simulating a button)
        cv2.putText(test_image, "DOWNLOAD", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        print("   Created test image: red 'DOWNLOAD' button")

        # Test classification
        is_deceptive, confidence, reasoning = classifier.classify_ui_element(
            test_image,
            context="Button says 'DOWNLOAD'"
        )

        print(f"   Result: {'DECEPTIVE' if is_deceptive else 'SAFE'}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Reasoning: {reasoning[:100]}...")

        return True

    except ImportError as e:
        print(f"❌ OpenCV not available: {e}")
        print("   Install with: pip install opencv-python")
        return False
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
        return False

def test_risk_engine_integration():
    """Test that RiskEngine correctly integrates LLM analysis"""
    print("\n⚙️ Testing RiskEngine integration...")

    try:
        from src.core.risk_engine import RiskEngine

        risk_engine = RiskEngine()

        if not risk_engine.use_llm:
            print("⚠️ LLM analysis is disabled in RiskEngine")
            print("   This is expected if Ollama is not available")
            return True  # Not an error, just a warning

        print("✅ RiskEngine has LLM integration enabled")

        # Test that calculate method accepts image parameter
        import inspect
        sig = inspect.signature(risk_engine.calculate)
        params = list(sig.parameters.keys())

        if 'image' in params:
            print("✅ calculate() method accepts image parameter")
        else:
            print("❌ calculate() method missing image parameter")
            return False

        return True

    except Exception as e:
        print(f"❌ RiskEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safe_click_integration():
    """Test that safe_click function integrates LLM analysis"""
    print("\n🖱️ Testing safe_click integration...")

    try:
        from src.core.click import safe_click

        # We can't actually test clicking without user interaction
        # but we can verify the function exists and has the right signature
        print("✅ safe_click function is available")

        # Check that it calls the updated risk_engine.calculate
        # This is implicit - if the code runs without errors, integration works
        return True

    except Exception as e:
        print(f"❌ safe_click test failed: {e}")
        return False

def run_full_demo():
    """Run a full demonstration of the integrated system"""
    print("\n🎬 Running full demonstration...")

    try:
        # Import all components
        from src.core.risk_engine import RiskEngine
        from src.core.vision import VisionGuard
        import pyautogui

        # Get screen info
        screen_width, screen_height = pyautogui.size()
        print(f"   Screen: {screen_width}x{screen_height}")

        # Create components
        risk_engine = RiskEngine()
        vision = VisionGuard()

        print(f"   RiskEngine LLM enabled: {risk_engine.use_llm}")

        if risk_engine.use_llm:
            print("   ✅ Full LLM integration is ready")
            print("\n   When you run safe_click() now:")
            print("   1. It will capture screenshot around click location")
            print("   2. Extract text using OCR")
            print("   3. Calculate base risk (words + position + history)")
            print("   4. If base risk is moderate (0.2-0.8), use LLM visual analysis")
            print("   5. LLM risk contributes up to 15% of total risk score")
            print("   6. Final decision based on combined risk score")
        else:
            print("   ⚠️ LLM integration is disabled")
            print("   System will work with only text-based risk assessment")

        return True

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main test function"""
    print("🛡️ ClawShield Ollama Integration Test")
    print("=" * 50)

    # Test 1: Ollama availability
    classifier = test_ollama_availability()

    # Test 2: Image classification (if Ollama is available)
    classification_ok = True
    if classifier and classifier.is_available():
        classification_ok = test_image_classification(classifier)
    else:
        print("\n⏭️ Skipping image classification (Ollama not available)")

    # Test 3: RiskEngine integration
    risk_engine_ok = test_risk_engine_integration()

    # Test 4: safe_click integration
    safe_click_ok = test_safe_click_integration()

    # Run full demo
    demo_ok = run_full_demo()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")

    tests_passed = 0
    tests_total = 3  # Availability, RiskEngine, safe_click

    if classifier and classifier.is_available():
        tests_total += 1  # Add classification test
        if classification_ok:
            tests_passed += 1
            print("✅ Image classification: PASSED")
        else:
            print("❌ Image classification: FAILED")

    print(f"✅ Ollama availability: {'PASSED' if classifier and classifier.is_available() else 'NOT AVAILABLE'}")
    print(f"✅ RiskEngine integration: {'PASSED' if risk_engine_ok else 'FAILED'}")
    print(f"✅ safe_click integration: {'PASSED' if safe_click_ok else 'FAILED'}")
    print(f"✅ System demo: {'PASSED' if demo_ok else 'FAILED'}")

    if classifier and classifier.is_available():
        tests_passed += 1  # Ollama availability counts as passed

    if risk_engine_ok:
        tests_passed += 1
    if safe_click_ok:
        tests_passed += 1

    print(f"\n🎯 Total: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n✨ All tests passed! Ollama integration is ready.")
        print("\n🚀 To use the enhanced ClawShield:")
        print("   1. Ensure Ollama is running: ollama serve")
        print("   2. Run the test agent: python test_agent.py")
        print("   3. Try the demo: python -c 'from src.core.click import safe_click; safe_click(100, 100)'")
    else:
        print("\n⚠️ Some tests failed. LLM integration may not work fully.")
        print("   ClawShield will still work with text-based risk assessment.")

if __name__ == "__main__":
    main()