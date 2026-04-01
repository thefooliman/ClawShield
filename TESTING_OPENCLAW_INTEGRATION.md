# OpenClaw 集成测试指南

本指南详细说明如何在 macOS 和 Linux 环境中测试 ClawShield 与 OpenClaw 的集成。

## 📋 测试前提

### 环境要求
- **macOS 测试**: 验证集成逻辑和命令解析
- **Linux 测试**: 实际 OpenClaw 环境验证（虚拟机）
- **Python 3.12+**: 所有环境
- **OpenClaw**: 安装在 Linux 虚拟机中

### 测试目标
1. ✅ 验证 OpenClaw 命令解析
2. ✅ 测试包装器模式 (`clawshield run --wrap openclaw`)
3. ✅ 测试插件/中间件模式
4. ✅ 验证完整工作流程
5. ✅ Linux 环境适配

## 🍎 macOS 模拟测试

### 步骤 1: 安装依赖
```bash
# 在 macOS 项目目录中
pip install -r requirements.txt

# 安装 Tesseract OCR
brew install tesseract

# 可选：安装 Ollama 进行视觉 AI 测试
brew install ollama
ollama pull llava
ollama serve
```

### 步骤 2: 运行模拟测试
```bash
# 1. 测试 OpenClaw 命令解析和集成逻辑
python test_openclaw_integration_macos.py

# 2. 测试 OpenClaw 模拟器
python test_openclaw_simulator.py click 100 200

# 3. 测试 ClawShield CLI
chmod +x clawshield
./clawshield test
./clawshield demo
```

### 步骤 3: 测试包装器模式
```bash
# 使用模拟的 OpenClaw 命令测试包装器
./clawshield run --wrap openclaw "click 100 200"

# 测试复杂命令格式
./clawshield run --wrap openclaw "mouse click 300 400"
./clawshield run --wrap openclaw "click(500, 600)"
```

### macOS 测试预期结果
- ✅ 命令解析正确识别 `click 100 200` 格式
- ✅ 包装器能拦截点击命令
- ✅ 插件模式提供正确的钩子接口
- ⚠️ 实际点击可能失败（因为没有真实 OpenClaw）
- ⚠️ macOS 原生对话框会弹出（需手动关闭）

## 🐧 Linux 环境适配

### 适配需求
ClawShield 包含 macOS 特有组件，需要在 Linux 上替换：

| 组件 | macOS | Linux 替代方案 |
|------|-------|---------------|
| 原生对话框 | `osascript` | `zenity` (GNOME) / `kdialog` (KDE) / `tkinter` |
| 框架依赖 | `pyobjc-framework-AppKit` | 移除或条件导入 |
| OCR 引擎 | `brew install tesseract` | `apt install tesseract-ocr` |

### 步骤 1: 创建 Linux 适配分支
```bash
# 在 macOS 上创建适配分支
git checkout -b linux-adaptation

# 创建平台兼容的对话框模块
```

### 步骤 2: 修改对话框代码
创建 `src/core/dialog.py` 实现跨平台对话框：

```python
import platform
import subprocess
import sys

def show_confirmation_dialog(message, title="ClawShield Security Alert"):
    """跨平台确认对话框"""
    system = platform.system()

    if system == "Darwin":  # macOS
        cmd = f'''osascript -e 'display dialog "{message}" buttons {{"Block", "Allow"}} default button "Block" with icon caution''''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return "Allow" in result.stdout

    elif system == "Linux":
        # 尝试 zenity (GNOME)
        try:
            cmd = ['zenity', '--question', '--text', message, '--title', title,
                   '--ok-label=Allow', '--cancel-label=Block']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            # 尝试 kdialog (KDE)
            try:
                cmd = ['kdialog', '--yesno', message, '--title', title,
                       '--yes-label', 'Allow', '--no-label', 'Block']
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
            except FileNotFoundError:
                # 回退到 tkinter (跨平台但需要 GUI)
                try:
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()
                    root.withdraw()  # 隐藏主窗口
                    result = messagebox.askyesno(title, message)
                    root.destroy()
                    return result
                except:
                    # 最后回退到控制台确认
                    print(f"⚠️ {title}: {message}")
                    response = input("Allow? (y/n): ").lower().strip()
                    return response in ['y', 'yes']

    elif system == "Windows":
        # Windows 实现
        import ctypes
        return ctypes.windll.user32.MessageBoxW(0, message, title, 4) == 6

    else:
        # 未知平台，使用控制台
        print(f"⚠️ {title}: {message}")
        response = input("Allow? (y/n): ").lower().strip()
        return response in ['y', 'yes']
```

### 步骤 3: 修改 click.py 使用跨平台对话框
```python
# 替换 osascript 调用
from .dialog import show_confirmation_dialog

# 在 safe_click 函数中替换
# 原代码:
# cmd = f'display dialog "{msg}. Proceed?" buttons {{"Block", "Allow"}} default button "Block" with icon caution'
# response = os.popen(f"osascript -e '{cmd}'").read()

# 新代码:
allowed = show_confirmation_dialog(f"{msg}. Proceed?")
if allowed:
    # 用户允许
```

### 步骤 4: 更新 requirements.txt
```txt
# 移除 macOS 特有依赖
# pyobjc-framework-AppKit>=12.0  # 仅 macOS

# 添加跨平台依赖
tkinter  # Python 内置，但可能需要系统包
```

### 步骤 5: 创建 Linux 安装脚本
创建 `scripts/install_linux.sh`:

```bash
#!/bin/bash
# Linux 依赖安装脚本

# 系统更新
sudo apt update
sudo apt upgrade -y

# 安装 Tesseract OCR
sudo apt install -y tesseract-ocr tesseract-ocr-eng

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 GUI 工具 (可选)
sudo apt install -y zenity kdialog

# 安装 Ollama (可选)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llava

echo "✅ Linux 依赖安装完成"
```

## 🔄 项目迁移到 Linux 虚拟机

### 方法 A: 使用打包脚本
我们提供了专门的打包脚本 `package_for_linux.sh`，它会自动处理所有排除项并生成完整的压缩包。

```bash
# 在 macOS 上使用打包脚本
cd /Users/admin/ClawShield
chmod +x package_for_linux.sh
./package_for_linux.sh

# 脚本会自动:
# 1. 清理缓存文件 (__pycache__, *.pyc 等)
# 2. 创建压缩包到 dist/ 目录
# 3. 显示压缩包大小和内容概览
# 4. 提供详细的传输说明

# 复制到 Linux 虚拟机 (使用脚本输出的实际文件名)
scp dist/clawshield-linux-*.tar.gz user@linux-vm:~/clawshield/

# 在 Linux 中解压
ssh user@linux-vm
cd ~/clawshield
tar -xzf clawshield-linux-*.tar.gz
cd clawshield-linux-*  # 进入解压后的目录
```

**打包脚本特性:**
- ✅ 自动清理 Python 缓存文件
- ✅ 排除虚拟环境、Git 目录、系统文件
- ✅ 生成详细的排除列表和打包信息
- ✅ 显示压缩包大小和内容概览
- ✅ 提供多种传输方法 (SCP, SFTP, 共享文件夹, HTTP)
- ✅ 包含完整的 Linux 适配组件

### 方法 B: 使用 Git 同步
```bash
# 在 Linux 中克隆仓库
git clone https://github.com/thefooliman/ClawShield.git
cd ClawShield
git checkout linux-adaptation  # 切换到适配分支
```

### 方法 C: 共享文件夹 (VMware/VirtualBox)
1. 设置共享文件夹: macOS 目录 → Linux 虚拟机
2. 在 Linux 中挂载共享文件夹
3. 直接访问项目文件

## 🧪 Linux 环境测试

### 步骤 1: 安装 Linux 依赖
```bash
# 在 Linux 虚拟机中
cd ~/clawshield
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
```

### 步骤 1.5: 验证兼容性
安装完成后，运行兼容性测试确保所有组件正常工作：

```bash
# 运行 Linux 兼容性测试
python test_linux_compatibility.py

# 预期输出:
# 🧪 ClawShield Linux 兼容性测试
# ==================================================
# 🔍 测试 Python 导入...
# ✅ cv2 (opencv-python)
# ✅ pytesseract (pytesseract)
# ✅ pyautogui (pyautogui)
# ✅ requests (requests)
# ✅ PIL (Pillow)
# ...
# 📊 测试总结
# ==================================================
# ✅ 导入测试
# ✅ 平台测试
# ✅ 对话框测试
# ✅ OpenClaw 集成测试
# 🎯 通过率: 4/4 (100.0%)
```

如果测试失败，请检查:
1. 虚拟环境是否正确激活: `source venv/bin/activate`
2. 依赖是否完整安装: `pip install -r requirements.txt`
3. 系统工具是否安装: `tesseract --version`, `zenity --version`

### 步骤 2: 验证 ClawShield 基础功能
```bash
# 测试 OCR 功能
python -c "from src.core.vision import VisionGuard; v = VisionGuard(); print('✅ VisionGuard 初始化正常')"

# 测试风险引擎
python -c "from src.core.risk_engine import RiskEngine; r = RiskEngine(); print('✅ RiskEngine 初始化正常')"

# 测试对话框系统
python -c "from src.core.dialog import show_confirmation_dialog; print('✅ 对话框系统正常')"
```

### 步骤 3: 测试 OpenClaw 集成
```bash
# 假设 OpenClaw 已安装在 Linux 中
which openclaw

# 测试包装器模式
./clawshield run --wrap openclaw "click 100 200"

# 测试真实 OpenClaw 命令
openclaw click 100 200  # 直接执行
./clawshield run --wrap openclaw click 100 200  # 通过 ClawShield 执行
```

### 步骤 4: 端到端测试场景
```bash
# 场景 1: 安全点击 (屏幕边缘)
./clawshield run --wrap openclaw click 50 50

# 场景 2: 高风险点击 (屏幕中心，模拟危险按钮)
./clawshield run --wrap openclaw click 960 540  # 假设 1920x1080 屏幕中心

# 场景 3: 批量点击测试
./clawshield run --wrap openclaw "click 100 100; click 200 200; click 300 300"
```

## 📊 测试验证清单

### 核心功能验证
- [ ] OpenClaw 命令解析正确 (`click 100 200` 格式)
- [ ] 包装器模式拦截点击命令
- [ ] 四因子风险评估正常计算
- [ ] 跨平台对话框工作正常
- [ ] 历史信任记录持久化

### 集成验证
- [ ] ClawShield CLI 与 OpenClaw 命令兼容
- [ ] 插件模式提供正确的钩子接口
- [ ] 执行报告包含详细统计
- [ ] 错误处理优雅降级

### 性能验证
- [ ] 点击拦截延迟 < 500ms
- [ ] 内存使用稳定
- [ ] 多命令批处理正常
- [ ] 长时间运行无内存泄漏

## 🐛 常见问题排查

### 问题 1: OpenClaw 命令无法解析
**症状**: `intercepted_clicks: 0` 但命令包含点击
**解决**: 检查命令格式，更新 `_extract_clicks()` 方法中的正则表达式

### 问题 2: Linux 对话框不显示
**症状**: 直接通过/失败，无用户确认
**解决**:
1. 安装 `zenity`: `sudo apt install zenity`
2. 或安装 `kdialog`: `sudo apt install kdialog`
3. 检查 `show_confirmation_dialog()` 回退逻辑

### 问题 3: OCR 失败
**症状**: `text` 为空或乱码
**解决**:
1. 确认 Tesseract 安装: `tesseract --version`
2. 安装语言包: `sudo apt install tesseract-ocr-eng`
3. 调整截图区域大小

### 问题 4: Ollama 连接失败
**症状**: `LLM analysis disabled`
**解决**:
1. 确认 Ollama 运行: `ollama serve`
2. 检查模型: `ollama list`
3. 测试连接: `curl http://localhost:11434/api/tags`

## 📈 测试报告模板

```markdown
# OpenClaw 集成测试报告

## 测试环境
- 系统: Ubuntu 22.04 LTS
- Python: 3.12.0
- OpenClaw: v2.1.0
- ClawShield: v1.0

## 测试结果
| 测试项目 | 状态 | 备注 |
|----------|------|------|
| 命令解析 | ✅ | 正确识别 `click 100 200` 格式 |
| 包装器模式 | ✅ | 拦截 10/10 点击命令 |
| 风险评估 | ✅ | 四因子评分计算正常 |
| 对话框 | ✅ | zenity 对话框正常显示 |
| CLI 集成 | ✅ | `clawshield run --wrap` 工作正常 |

## 性能指标
- 平均拦截延迟: 320ms
- 内存占用: 45MB
- 点击成功率: 100%

## 问题发现
1. 无

## 建议
1. 添加 OpenClaw 命令格式文档
2. 优化 Linux 对话框回退逻辑
```

## 🚀 下一步

完成 Linux 测试后:

1. **提交代码**: 将 Linux 适配分支合并到主分支
2. **更新文档**: 补充 Linux 安装和使用说明
3. **发布版本**: 标记 v1.0 正式版
4. **持续集成**: 添加 macOS/Linux 自动化测试
5. **扩展支持**: 考虑 Windows 和其他自动化框架集成

---

**测试支持**: 如遇问题，请提供:
1. 错误日志和堆栈跟踪
2. 系统环境信息 (`uname -a`, `python --version`)
3. OpenClaw 版本和命令示例
4. 测试步骤和预期/实际结果