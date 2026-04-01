#!/bin/bash
# Linux 依赖安装脚本
# 适用于 Ubuntu/Debian 系统

set -e  # 出错时退出

echo "🛡️  ClawShield Linux 依赖安装脚本"
echo "========================================"

# 检查系统
if [ ! -f /etc/os-release ]; then
    echo "❌ 无法检测操作系统"
    exit 1
fi

. /etc/os-release
echo "📱 操作系统: $NAME $VERSION"
echo "🐧 架构: $(uname -m)"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    echo "📦 安装 Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

echo "✅ Python3 版本: $(python3 --version)"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "📦 安装 pip3..."
    sudo apt update
    sudo apt install -y python3-pip
fi

echo "✅ pip3 版本: $(pip3 --version)"

# 系统更新
echo "🔄 更新系统包..."
sudo apt update
sudo apt upgrade -y

# 安装系统依赖
echo "📦 安装系统依赖..."

# Tesseract OCR
echo "🔤 安装 Tesseract OCR..."
sudo apt install -y tesseract-ocr tesseract-ocr-eng

# 检查安装结果
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract 安装失败，尝试替代方法..."
    # 尝试从源码安装
    sudo apt install -y libleptonica-dev libtesseract-dev tesseract-ocr
fi

echo "✅ Tesseract 版本: $(tesseract --version 2>/dev/null | head -n1 || echo '未知')"

# 安装 GUI 工具 (用于对话框)
echo "🖥️  安装 GUI 工具..."
if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    sudo apt install -y zenity kdialog x11-utils

    # 检查桌面环境
    if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ] || [ "$XDG_CURRENT_DESKTOP" = "ubuntu:GNOME" ]; then
        echo "✅ GNOME 桌面环境检测到 (使用 zenity)"
    elif [ "$XDG_CURRENT_DESKTOP" = "KDE" ]; then
        echo "✅ KDE 桌面环境检测到 (使用 kdialog)"
    else
        echo "⚠️  未知桌面环境，已安装 zenity 和 kdialog"
    fi
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    sudo dnf install -y zenity kdialog
elif command -v pacman &> /dev/null; then
    # Arch
    sudo pacman -S --noconfirm zenity kdialog
fi

# 安装开发工具
echo "🔧 安装开发工具..."
sudo apt install -y build-essential python3-dev libgtk-3-dev

# 安装 Python 虚拟环境
echo "🐍 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装 Python 包
echo "📦 安装 Python 依赖..."
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装 requirements.txt 中的依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python 依赖安装完成"
else
    echo "❌ requirements.txt 未找到"
    exit 1
fi

# 安装额外的 Python 包 (用于跨平台支持)
echo "➕ 安装额外 Python 包..."
pip install pyautogui  # 确保 pyautogui 正确安装
pip install opencv-python-headless  # 无头模式 OpenCV（可选）

# 验证安装
echo "🔍 验证安装..."

# 测试 Python 导入
echo "🧪 测试 Python 导入..."
cat > /tmp/test_imports.py << 'EOF'
try:
    import cv2
    print("✅ OpenCV 导入正常")
except ImportError as e:
    print(f"❌ OpenCV 导入失败: {e}")

try:
    import pytesseract
    print("✅ pytesseract 导入正常")
except ImportError as e:
    print(f"❌ pytesseract 导入失败: {e}")

try:
    import pyautogui
    print("✅ pyautogui 导入正常")
except ImportError as e:
    print(f"❌ pyautogui 导入失败: {e}")

try:
    import requests
    print("✅ requests 导入正常")
except ImportError as e:
    print(f"❌ requests 导入失败: {e}")
EOF

python3 /tmp/test_imports.py
rm /tmp/test_imports.py

# 测试 Tesseract
echo "🧪 测试 Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract --version | head -n1
    echo "✅ Tesseract 正常工作"
else
    echo "❌ Tesseract 未安装或不可用"
fi

# 测试 GUI 工具
echo "🧪 测试 GUI 工具..."
if command -v zenity &> /dev/null; then
    echo "✅ zenity 可用"
else
    echo "⚠️  zenity 不可用，对话框将使用控制台回退"
fi

if command -v kdialog &> /dev/null; then
    echo "✅ kdialog 可用"
else
    echo "⚠️  kdialog 不可用"
fi

# 安装完成
echo ""
echo "========================================"
echo "✨ ClawShield Linux 安装完成！"
echo ""
echo "🚀 下一步操作:"
echo ""
echo "1. 激活虚拟环境:"
echo "   source venv/bin/activate"
echo ""
echo "2. 测试 ClawShield:"
echo "   python test_ollama_integration.py"
echo "   ./clawshield test"
echo ""
echo "3. 安装 Ollama (可选，用于视觉 AI):"
echo "   curl -fsSL https://ollama.com/install.sh | sh"
echo "   ollama pull llava"
echo "   ollama serve"
echo ""
echo "4. 运行演示:"
echo "   ./clawshield demo"
echo ""
echo "5. 测试 OpenClaw 集成:"
echo "   ./clawshield run --wrap openclaw 'click 100 200'"
echo ""
echo "📝 注意:"
echo "- 确保 OpenClaw 已安装在系统中"
echo "- 如果需要 Windows 支持，请安装 tkinter: sudo apt install python3-tk"
echo "- 对于无头服务器，对话框将自动回退到控制台界面"
echo "========================================"

# 创建快捷脚本
cat > /tmp/clawshield_launcher.sh << 'EOF'
#!/bin/bash
# ClawShield 启动器脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "⚠️  虚拟环境未找到，使用系统 Python"
fi

# 执行命令
exec python -m src.cli "$@"
EOF

chmod +x /tmp/clawshield_launcher.sh
mv /tmp/clawshield_launcher.sh ./clawshield_linux 2>/dev/null || true

if [ -f "./clawshield_linux" ]; then
    echo ""
    echo "📂 已创建 Linux 启动脚本: ./clawshield_linux"
    echo "   用法: ./clawshield_linux [command]"
fi

echo ""
echo "✅ 安装脚本完成"
exit 0