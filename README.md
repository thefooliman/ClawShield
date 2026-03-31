# 🛡️ ClawShield (v0.4)
**A Hybrid AI Security Sentry for Autonomous Agents. Stop accidental clicks before they happen.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

ClawShield is a hybrid AI security layer that prevents autonomous agents from performing high-risk operations (unintended deletions, payments, subscriptions, deceptive buttons) through real-time multi-factor risk assessment combining OCR, visual AI, and contextual analysis.

## ✨ Key Features

- **Multi-Factor Risk Scoring**: 4-factor assessment (keywords, position, history, visual AI)
- **Local Vision AI**: Ollama integration for detecting deceptive UI elements
- **Historical Trust Building**: Actions become trusted after repeated safe use
- **Adaptive Thresholds**: Dynamic risk-based decision making (high/medium/low risk)
- **Native macOS Integration**: Seamless user confirmation dialogs
- **Real-time Visual Audit**: Live screen analysis with OCR and AI
- **Lightweight & Fast**: Efficient risk assessment with intelligent LLM triggering

---

## 🚀 How it Works (v0.4 Hybrid AI System)

1. **Target Capture**: Intercepts click coordinates $(x, y)$ from AI agent or user.
2. **Visual Context Capture**: Crops a $200 \times 200$ pixel region around cursor for UI analysis.
3. **Multi-Modal Analysis**:
   - **OCR Text Extraction**: Uses Tesseract to extract UI text
   - **Visual AI Classification**: Local LLM (Ollama) analyzes button appearance for deception
   - **Contextual Assessment**: Screen position, historical trust patterns
4. **Four-Factor Risk Assessment**:
   - **Keyword Matching** (50%): Weighted dangerous words (Delete=1.0, Confirm=0.9, etc.)
   - **Position Risk** (25%): Clicks near screen center are higher risk
   - **Historical Trust** (10%): Previously allowed actions gain trust
   - **LLM Visual Risk** (15%): AI-based deception detection
5. **Adaptive Decision Making**:
   - **High Risk (>0.7)**: macOS native dialog for user confirmation
   - **Medium Risk (0.3-0.7)**: Warning but automatic execution
   - **Low Risk (<0.3)**: Direct pass with logging

### 📐 The Risk Formula
The hybrid risk score $R$ combines four factors:
$$R = 0.5 \times R_{\text{words}} + 0.25 \times R_{\text{position}} + 0.1 \times R_{\text{history}} + 0.15 \times R_{\text{LLM}}$$

Where:
- $R_{\text{words}}$: Weighted sum of dangerous keywords in detected text
- $R_{\text{position}}$: Normalized distance from screen center (closer = higher risk)
- $R_{\text{history}}$: Trust factor based on previous interactions (negative = trusted)
- $R_{\text{LLM}}$: Visual deception score from local LLM analysis (0-1)

---

## 🛠️ Installation

### 1. Install System Dependencies

#### OCR Engine (Tesseract)
ClawShield requires Tesseract for text recognition:
```bash
brew install tesseract
```

#### Local AI Model (Ollama - Optional but recommended)
For visual deception detection using local LLM:
```bash
# Install Ollama
brew install ollama

# Pull a vision model (llava recommended)
ollama pull llava

# Start Ollama service (keep this running)
ollama serve
```

### 2. Setup Project Environment
```bash
# Clone the repo
git clone [https://github.com/thefooliman/ClawShield.git](https://github.com/thefooliman/ClawShield.git)
cd ClawShield

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 📖 Usage

### Test Ollama Integration
First, verify that the local AI vision model is working:
```bash
python test_ollama_integration.py
```
This will check Ollama availability and test the visual classification system.

### Run AI Agent Simulation
Simulate an autonomous AI agent exploring the screen:
```bash
python test_agent.py
```
Choose the guided demo to see ClawShield in action:
- Safe clicks in neutral areas
- Dangerous button interception
- Trust building through repeated allowances
- Random exploration with real-time protection

### Real-time Protection Mode
Run the live protection system that monitors mouse movements:
```bash
# Set Python path
export PYTHONPATH=$PYTHONPATH:.

# Start the sentinel
python src/main.py
```
- Move your mouse over UI elements
- Press 'q' to quit
- See real-time risk assessment in the overlay window

### Integration in Your Code
Use ClawShield's `safe_click()` function in your AI agent code:
```python
from src.core.click import safe_click

# Replace direct clicks with safe_click
if safe_click(x, y):
    print("Click executed safely")
else:
    print("Click was blocked by risk assessment")
```

### Testing with Dangerous UI Elements
1. Open a webpage with "Delete", "Confirm", or "Subscribe" buttons
2. Run the test agent or main script
3. Hover over dangerous buttons to see interception
4. Observe the macOS native dialog for high-risk actions

---

## 🗺️ Roadmap
- [x] Phase 0: Basic OCR + Keyword matching + Native Dialog (MVP)
- [x] Phase 1: Local Vision LLM (Ollama) integration with multi-factor risk scoring
- [ ] Phase 2: OpenClaw Protocol integration for universal Agent control.

---

## 🤝 Contributing
This is an open-source project created by a high school developer. Feel free to open issues or submit pull requests!

## 📄 License
This project is licensed under the MIT License.