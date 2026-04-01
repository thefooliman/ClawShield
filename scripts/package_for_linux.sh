#!/bin/bash
# ClawShield Linux 项目打包脚本
# 在 macOS 上运行，将项目打包以便传输到 Linux 虚拟机

set -e

echo "📦 ClawShield Linux 项目打包工具"
echo "========================================"

# 项目根目录
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_DIR"

echo "📁 项目目录: $PROJECT_DIR"

# 检查是否为 macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "⚠️  此脚本应在 macOS 上运行"
    echo "   如果你在 Linux 上，请直接运行 scripts/install_linux.sh"
    read -p "继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
PACKAGE_NAME="clawshield-linux-$(date +%Y%m%d-%H%M%S)"
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

echo "📂 创建临时目录: $PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# 需要包含的文件和目录
INCLUDE_PATTERNS=(
    "src/"
    "scripts/"
    "requirements.txt"
    "clawshield"
    "test_*.py"
    "*.md"
    "LICENSE"
    ".gitignore"
)

# 需要排除的文件和目录
EXCLUDE_PATTERNS=(
    "__pycache__"
    "*.pyc"
    "*.pyo"
    ".DS_Store"
    "venv/"
    ".git/"
    "*.log"
    "clawshield_history.json"
    "clawshield_trust.json"
    "assets/"  # 临时排除，如果需要可以调整
)

echo "📋 复制文件..."

# 使用 rsync 复制文件
for pattern in "${INCLUDE_PATTERNS[@]}"; do
    if [ -e "$pattern" ]; then
        echo "  复制: $pattern"
        rsync -a --include="*/" --include="*" --exclude="*" \
            --exclude-from=<(printf "%s\n" "${EXCLUDE_PATTERNS[@]}") \
            "$pattern" "$PACKAGE_DIR/"
    else
        echo "  ⚠️  文件不存在: $pattern"
    fi
done

# 创建 README-LINUX.md
cat > "$PACKAGE_DIR/README-LINUX.md" << 'EOF'
# ClawShield Linux 部署指南

## 📦 文件说明

此包包含 ClawShield v1.0 (OpenClaw Security Middleware) 的 Linux 适配版本。

### 主要变更
1. ✅ 跨平台对话框支持 (zenity/kdialog/tkinter/控制台回退)
2. ✅ 移除 macOS 特有依赖 (pyobjc-framework-AppKit)
3. ✅ Linux 安装脚本
4. ✅ OpenClaw 集成测试工具

### 目录结构
```
clawshield-linux/
├── src/                    # 源代码
├── scripts/               # 安装和工具脚本
├── requirements.txt       # Python 依赖
├── clawshield            # CLI 入口点
├── test_*.py             # 测试脚本
├── README.md             # 主文档
├── README-LINUX.md       # Linux 特定文档 (本文件)
└── LICENSE               # MIT 许可证
```

## 🚀 快速开始

### 1. 安装系统依赖
```bash
# 进入项目目录
cd clawshield-linux

# 运行安装脚本
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
```

### 2. 激活虚拟环境
```bash
source venv/bin/activate
```

### 3. 测试安装
```bash
# 测试基础功能
./clawshield test

# 测试 OpenClaw 集成
./clawshield run --wrap openclaw "click 100 200"
```

### 4. 安装 Ollama (可选)
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取视觉模型
ollama pull llava

# 启动服务
ollama serve
```

## 🔧 配置 OpenClaw

### 方法 A: 包装器模式
```bash
# 使用 ClawShield 包装 OpenClaw 命令
./clawshield run --wrap openclaw "click 100 200"
./clawshield run --wrap openclaw "mouse click 300 400"
```

### 方法 B: 脚本包装
创建 wrapper.sh:
```bash
#!/bin/bash
cd /path/to/clawshield-linux
source venv/bin/activate
./clawshield run --wrap openclaw "$@"
```

## 🐛 故障排除

### 问题: Tesseract OCR 失败
```bash
# 重新安装 Tesseract
sudo apt install --reinstall tesseract-ocr tesseract-ocr-eng

# 测试 Tesseract
tesseract --version
```

### 问题: 对话框不显示
```bash
# 安装 GUI 工具
sudo apt install zenity kdialog

# 测试 zenity
zenity --info --text="测试对话框"
```

### 问题: Python 导入错误
```bash
# 重新安装虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 支持

- GitHub: https://github.com/thefooliman/ClawShield
- 问题: 查看 README.md 中的故障排除部分
- 文档: 完整的用户指南在 README.md

## 📄 许可证

MIT License - 详见 LICENSE 文件
EOF

# 创建压缩包
echo "🗜️  创建压缩包..."
cd "$TEMP_DIR"
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

# 移动回项目目录
mv "$PACKAGE_NAME.tar.gz" "$PROJECT_DIR/"

# 清理临时目录
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "✅ 打包完成!"
echo ""
echo "📦 压缩包: $PROJECT_DIR/$PACKAGE_NAME.tar.gz"
echo ""
echo "🚀 传输到 Linux 虚拟机:"
echo ""
echo "方法 A: SCP 传输"
echo "  scp '$PROJECT_DIR/$PACKAGE_NAME.tar.gz' user@linux-vm:~/"
echo ""
echo "方法 B: 共享文件夹"
echo "  1. 在虚拟机设置中启用共享文件夹"
echo "  2. 将压缩包复制到共享目录"
echo "  3. 在 Linux 中访问共享文件夹"
echo ""
echo "方法 C: USB 驱动器"
echo "  1. 将压缩包复制到 USB 驱动器"
echo "  2. 在 Linux 中挂载 USB 驱动器"
echo "  3. 复制文件到 Linux 系统"
echo ""
echo "📋 在 Linux 中的安装步骤:"
echo ""
echo "1. 解压文件:"
echo "   tar -xzf $PACKAGE_NAME.tar.gz"
echo "   cd $PACKAGE_NAME"
echo ""
echo "2. 运行安装脚本:"
echo "   chmod +x scripts/install_linux.sh"
echo "   ./scripts/install_linux.sh"
echo ""
echo "3. 测试安装:"
echo "   source venv/bin/activate"
echo "   ./clawshield test"
echo ""
echo "4. 集成 OpenClaw:"
echo "   ./clawshield run --wrap openclaw 'click 100 200'"
echo ""
echo "========================================"
echo ""
echo "📝 注意:"
echo "- 确保 Linux 虚拟机已安装 OpenClaw"
echo "- 对于无头服务器，对话框将使用控制台回退"
echo "- 如果需要 GUI，请安装 zenity 或 kdialog"
echo "- 查看 README-LINUX.md 获取详细说明"
echo ""
echo "✅ 打包脚本完成"
exit 0