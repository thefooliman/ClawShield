#!/bin/bash
# ClawShield Linux 项目打包脚本
# 在 macOS 上运行，将项目打包以便传输到 Linux 虚拟机

set -e  # 出错时退出

echo "📦 ClawShield Linux 项目打包脚本"
echo "========================================"
echo ""

# 检查当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
echo "📁 项目根目录: $PROJECT_ROOT"

# 检查是否在正确的目录中
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "❌ 错误: 未找到 requirements.txt，请确保在 ClawShield 项目根目录中运行"
    exit 1
fi

# 获取版本信息（如果有）
VERSION="1.0"
if [ -f "$PROJECT_ROOT/VERSION" ]; then
    VERSION=$(cat "$PROJECT_ROOT/VERSION")
elif [ -f "$PROJECT_ROOT/version.txt" ]; then
    VERSION=$(cat "$PROJECT_ROOT/version.txt")
fi

echo "📊 项目版本: $VERSION"
echo ""

# 清理缓存文件
echo "🧹 清理缓存文件..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name ".DS_Store" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.log" -delete 2>/dev/null || true
echo "✅ 缓存文件清理完成"
echo ""

# 计算项目大小（排除需要忽略的目录）
echo "📊 计算项目大小..."
PROJECT_SIZE=$(find "$PROJECT_ROOT" -type f \
    -not -path "*/venv/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.DS_Store" \
    -not -path "*/assets/screenshots/*" \
    -not -name "*.pyc" \
    -not -name "*.log" \
    -exec stat -f%z {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")

if [ "$PROJECT_SIZE" = "0" ]; then
    PROJECT_SIZE=$(find "$PROJECT_ROOT" -type f \
        -not -path "*/venv/*" \
        -not -path "*/.git/*" \
        -not -path "*/__pycache__/*" \
        -exec wc -c {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
fi

HUMAN_SIZE=$(numfmt --to=iec --suffix=B "$PROJECT_SIZE" 2>/dev/null || echo "${PROJECT_SIZE}B")
echo "📁 项目大小 (排除venv/.git): $HUMAN_SIZE"
echo ""

# 创建输出目录
OUTPUT_DIR="$PROJECT_ROOT/dist"
mkdir -p "$OUTPUT_DIR"
echo "📂 输出目录: $OUTPUT_DIR"

# 生成打包文件名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="clawshield-linux-v${VERSION}-${TIMESTAMP}"
PACKAGE_FILE="$OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"

echo "📦 创建压缩包: $(basename "$PACKAGE_FILE")"
echo ""

# 创建排除文件列表
EXCLUDE_FILE="$OUTPUT_DIR/exclude_list.txt"
cat > "$EXCLUDE_FILE" << 'EOF'
# ClawShield 打包排除列表
# 自动生成于 $(date)

# 虚拟环境
venv/

# Git 相关
.git/
.gitignore
.gitmodules

# 系统文件
.DS_Store
Thumbs.db

# Python 缓存
__pycache__/
*.pyc
*.pyo
*.pyd

# 环境文件
.env
.env.local
.env.*.local

# 日志文件
*.log
logs/

# 测试截图
assets/screenshots/

# 构建输出
dist/
build/
*.egg-info/

# IDE 文件
.vscode/
.idea/
*.swp
*.swo

# macOS 特定
*.app/
EOF

echo "📝 排除列表已生成: $(basename "$EXCLUDE_FILE")"
echo ""

# 显示将要包含的主要文件
echo "📋 主要文件清单:"
find "$PROJECT_ROOT" -maxdepth 2 -type f \
    -not -path "*/venv/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -name "*.pyc" \
    -not -name ".DS_Store" \
    -not -name "*.log" \
    | head -20 | while read file; do
    echo "  📄 $(basename "$file")"
done

echo "  ... (更多文件)"
echo ""

# 创建压缩包
echo "🔄 正在创建压缩包..."
cd "$PROJECT_ROOT"

# 使用 tar 创建压缩包，排除不需要的文件
tar --exclude="venv" \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude=".DS_Store" \
    --exclude="dist" \
    --exclude="assets/screenshots" \
    --exclude="*.log" \
    -czf "$PACKAGE_FILE" .

if [ $? -eq 0 ]; then
    # 计算压缩包大小
    PACKAGE_SIZE=$(stat -f%z "$PACKAGE_FILE" 2>/dev/null || stat -c%s "$PACKAGE_FILE" 2>/dev/null || echo "0")
    PACKAGE_HUMAN_SIZE=$(numfmt --to=iec --suffix=B "$PACKAGE_SIZE" 2>/dev/null || echo "${PACKAGE_SIZE}B")

    echo "✅ 压缩包创建成功: $(basename "$PACKAGE_FILE")"
    echo "📦 压缩包大小: $PACKAGE_HUMAN_SIZE"
    echo ""

    # 显示压缩包内容概览
    echo "📋 压缩包内容概览:"
    tar -tzf "$PACKAGE_FILE" | head -20 | while read line; do
        echo "  📄 $line"
    done

    if [ $(tar -tzf "$PACKAGE_FILE" | wc -l) -gt 20 ]; then
        echo "  ... (更多文件)"
    fi
else
    echo "❌ 压缩包创建失败"
    exit 1
fi

echo ""
echo "========================================"
echo "✨ 打包完成！"
echo ""
echo "🚀 下一步操作:"
echo ""
echo "1. 传输到 Linux 虚拟机:"
echo "   scp \"$PACKAGE_FILE\" user@linux-vm:~/clawshield/"
echo ""
echo "2. 在 Linux 中解压:"
echo "   ssh user@linux-vm"
echo "   cd ~/clawshield"
echo "   tar -xzf \"$(basename "$PACKAGE_FILE")\""
echo "   cd \"${PACKAGE_NAME}\""
echo ""
echo "3. 安装依赖:"
echo "   chmod +x scripts/install_linux.sh"
echo "   ./scripts/install_linux.sh"
echo ""
echo "4. 测试 OpenClaw 集成:"
echo "   ./clawshield run --wrap openclaw 'click 100 200'"
echo ""
echo "📝 传输方法备选:"
echo ""
echo "A. SCP 传输:"
echo "   scp \"$PACKAGE_FILE\" user@linux-vm:/path/to/destination/"
echo ""
echo "B. SFTP 传输:"
echo "   sftp user@linux-vm"
echo "   put \"$PACKAGE_FILE\""
echo "   exit"
echo ""
echo "C. 共享文件夹 (VMware/VirtualBox):"
echo "   1. 将压缩包复制到共享文件夹"
echo "   2. 在 Linux 虚拟机中访问共享文件夹"
echo "   3. 解压到目标位置"
echo ""
echo "D. HTTP 服务器 (临时):"
echo "   # 在 macOS 上启动简单 HTTP 服务器"
echo "   cd \"$OUTPUT_DIR\""
echo "   python3 -m http.server 8080"
echo "   # 在 Linux 中下载:"
echo "   wget http://macos-ip:8080/$(basename "$PACKAGE_FILE")"
echo ""
echo "🔧 验证打包完整性:"
echo "   # 在 Linux 中验证"
echo "   tar -tzf \"$(basename "$PACKAGE_FILE")\" > /dev/null && echo '✅ 压缩包完整'"
echo ""
echo "📁 压缩包位置:"
echo "   $PACKAGE_FILE"
echo ""
echo "⏰ 打包时间: $(date)"
echo "========================================"
echo ""

# 保存打包信息
PACKAGE_INFO="$OUTPUT_DIR/${PACKAGE_NAME}.info"
cat > "$PACKAGE_INFO" << EOF
ClawShield Linux 打包信息
=======================

打包时间: $(date)
打包版本: v${VERSION}
打包标识: ${PACKAGE_NAME}

源目录: ${PROJECT_ROOT}
输出文件: ${PACKAGE_FILE}
文件大小: ${PACKAGE_HUMAN_SIZE}

排除内容:
- venv/ (Python虚拟环境)
- .git/ (Git版本控制)
- __pycache__/ (Python缓存)
- *.pyc (Python字节码)
- .DS_Store (macOS系统文件)
- assets/screenshots/ (测试截图)
- dist/ (构建输出目录)

包含的主要组件:
- src/ (源代码)
- scripts/ (脚本文件)
- requirements.txt (Python依赖)
- *.py (Python脚本)
- *.md (文档文件)
- TESTING_OPENCLAW_INTEGRATION.md (测试指南)

Linux 适配说明:
- 已添加跨平台对话框模块 (src/core/dialog.py)
- 已更新 click.py 使用跨平台对话框
- 已创建 Linux 安装脚本 (scripts/install_linux.sh)
- 已移除 macOS 特有依赖 (pyobjc-framework-AppKit)

传输建议:
1. 使用 SCP 传输到 Linux 虚拟机
2. 解压: tar -xzf ${PACKAGE_NAME}.tar.gz
3. 运行安装脚本: ./scripts/install_linux.sh
4. 测试: ./clawshield run --wrap openclaw 'click 100 200'

测试指南:
详见 TESTING_OPENCLAW_INTEGRATION.md
EOF

echo "📄 打包信息已保存: $(basename "$PACKAGE_INFO")"
echo ""
echo "✅ 打包脚本执行完成"
exit 0