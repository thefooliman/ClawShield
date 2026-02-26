# 🛡️ ClawShield (Phase 0)
**A Visual Security Sentry for AI Agents. Stop accidental clicks before they happen.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

ClawShield is a lightweight security layer designed to prevent AI Agents from performing high-risk operations (like unintended deletions, payments, or subscriptions) by performing a real-time visual audit before any click is executed.

---

## 🚀 How it Works (Phase 0 Logic)

1. **Target Capture**: The system intercepts the intended click coordinates $(x, y)$.
2. **Region Sampling**: It crops a $200 \times 200$ pixel region around the cursor to capture UI context.
3. **OCR Analysis**: Uses **Tesseract OCR** to extract text from the sampled image.
4. **Risk Assessment**: Matches extracted text against a "Danger List" (e.g., *Delete, Confirm, Pay*).
5. **Human-in-the-loop**: If a risk is detected, it triggers a **Native macOS Dialog** to ask for user permission.

### 📐 The Risk Formula
The system evaluates the risk $R$ based on the intersection of detected text $T$ and predefined danger set $D$:
$$R = \min(1, \sum_{word \in (T \cap D)} w_{word})$$
*Currently $w=1.0$ for any matching keyword in Phase 0.*

---

## 🛠️ Installation

### 1. Install OCR Engine (macOS)
ClawShield requires Tesseract to "read" the screen.
```bash
brew install tesseract
```

### 2. Setup Environment
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
To run the MVP demo:

```bash
# Ensure Python can find the src directory
export PYTHONPATH=$PYTHONPATH:.

# Execute the main script
python src/main.py
```

Steps to test:

1. Run the script.
2. You have 3 seconds to move your mouse over a "Delete" or "Pay" button (e.g., on a website).
3. ClawShield will scan the area and pop up a warning if a risk is detected.

---

## 🗺️ Roadmap
- [x] Phase 0: Basic OCR + Keyword matching + Native Dialog (MVP)
- [ ] Phase 1: Local Vision LLM (Ollama/Moondream) for semantic reasoning.
- [ ] Phase 2: OpenClaw Protocol integration for universal Agent control.

---

## 🤝 Contributing
This is an open-source project created by a high school developer. Feel free to open issues or submit pull requests!

## 📄 License
This project is licensed under the MIT License.