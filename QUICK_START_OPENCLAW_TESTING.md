# 🚀 OpenClaw 集成测试快速指南

基于你的选择：
- ✅ 测试环境: macOS 本地模拟
- ✅ 命令格式: `click 100 200`
- ✅ 集成模式: 包装器模式和插件模式都测试

## 📋 快速开始

### 步骤 1: 在 macOS 上运行模拟测试
```bash
# 1. 运行完整的集成测试
python test_openclaw_integration_macos.py

# 2. 测试 OpenClaw 命令模拟器
python test_openclaw_simulator.py click 100 200
python test_openclaw_simulator.py move 300 400

# 3. 测试 ClawShield CLI
./clawshield test
./clawshield demo
```

### 步骤 2: 测试 OpenClaw 包装器模式
```bash
# 使用模拟的 OpenClaw 命令测试包装器
./clawshield run --wrap openclaw "click 100 200"

# 测试不同命令格式
./clawshield run --wrap openclaw "mouse click 300 400"
./clawshield run --wrap openclaw "click(500, 600)"
```

### 步骤 3: 打包项目用于 Linux 测试
```bash
# 使用打包脚本创建 Linux 版本
./package_for_linux.sh

# 脚本会:
# 1. 自动清理缓存文件
# 2. 创建压缩包到 dist/ 目录
# 3. 显示传输说明

# 查看生成的压缩包
ls -lh dist/clawshield-linux-*.tar.gz
```

### 步骤 4: 传输到 Linux 虚拟机
```bash
# 方法 A: SCP 传输
scp dist/clawshield-linux-*.tar.gz user@linux-vm:~/clawshield/

# 方法 B: 共享文件夹 (VMware/VirtualBox)
# 将压缩包复制到共享文件夹，在 Linux 中访问

# 方法 C: Git 同步
# 在 Linux 中克隆仓库并切换到 linux-adaptation 分支
```

### 步骤 5: 在 Linux 中安装和测试
```bash
# 在 Linux 虚拟机中
cd ~/clawshield

# 解压项目
tar -xzf clawshield-linux-*.tar.gz
cd clawshield-linux-*

# 安装依赖
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh

# 测试兼容性
python test_linux_compatibility.py

# 测试 OpenClaw 集成
./clawshield run --wrap openclaw 'click 100 200'
```

## 🧪 测试场景

### 场景 1: 基本命令解析
```bash
# 测试 click 100 200 格式解析
python -c "from src.integration.openclaw_integration import OpenClawWrapper; w = OpenClawWrapper('echo'); print(w._extract_clicks(['click', '100', '200']))"
```

### 场景 2: 包装器拦截测试
```bash
# 模拟高风险点击 (屏幕中心)
./clawshield run --wrap openclaw "click 960 540"  # 1920x1080 屏幕中心

# 模拟安全点击 (屏幕边缘)
./clawshield run --wrap openclaw "click 50 50"
```

### 场景 3: 完整工作流程
1. OpenClaw 发送命令: `click 100 200`
2. ClawShield 拦截并解析命令
3. 提取坐标 (100, 200)
4. 应用四因子风险评估 (关键词、位置、历史、LLM 视觉)
5. 显示跨平台确认对话框
6. 记录执行结果

## 📊 预期结果

### macOS 模拟测试:
- ✅ 命令解析正确识别 `click 100 200` 格式
- ✅ 包装器能拦截点击命令
- ✅ 插件模式提供正确的钩子接口
- ⚠️ 实际点击可能失败 (因为没有真实 OpenClaw)
- ⚠️ macOS 原生对话框会弹出 (需手动关闭)

### Linux 实际测试:
- ✅ OpenClaw 命令通过 ClawShield 执行
- ✅ 跨平台对话框工作 (zenity/kdialog/控制台)
- ✅ 四因子风险评估正常计算
- ✅ 执行报告包含详细统计

## 🐛 故障排除

### 问题: OpenClaw 命令无法解析
**解决**: 检查命令格式，更新 `src/integration/openclaw_integration.py` 中的正则表达式

### 问题: Linux 对话框不显示
**解决**:
```bash
# 安装 GUI 工具
sudo apt install zenity kdialog

# 或测试控制台回退
python -c "from src.core.dialog import show_confirmation_dialog; print(show_confirmation_dialog('Test'))"
```

### 问题: Tesseract OCR 失败
**解决**:
```bash
# 安装 Tesseract
sudo apt install tesseract-ocr tesseract-ocr-eng

# 验证安装
tesseract --version
```

## 📁 关键文件说明

| 文件 | 用途 |
|------|------|
| `test_openclaw_integration_macos.py` | macOS 集成测试主脚本 |
| `test_openclaw_simulator.py` | OpenClaw 命令模拟器 |
| `src/integration/openclaw_integration.py` | OpenClaw 集成核心代码 |
| `src/core/dialog.py` | 跨平台对话框模块 |
| `scripts/install_linux.sh` | Linux 依赖安装脚本 |
| `package_for_linux.sh` | 项目打包脚本 |
| `test_linux_compatibility.py` | Linux 兼容性测试 |
| `TESTING_OPENCLAW_INTEGRATION.md` | 详细测试指南 |

## 📈 测试报告

测试完成后，参考 `TESTING_OPENCLAW_INTEGRATION.md` 中的模板创建测试报告:

```markdown
# OpenClaw 集成测试报告

## 测试环境
- 系统: Ubuntu 22.04 LTS / macOS 14.x
- Python: 3.12.0
- OpenClaw: v2.1.0 (模拟/实际)
- ClawShield: v1.0

## 测试结果
| 测试项目 | 状态 | 备注 |
|----------|------|------|
| 命令解析 | ✅ | 正确识别 `click 100 200` 格式 |
| 包装器模式 | ✅ | 拦截 N/N 点击命令 |
| 风险评估 | ✅ | 四因子评分计算正常 |
| 对话框 | ✅ | 跨平台对话框正常 |
| CLI 集成 | ✅ | `clawshield run --wrap` 工作正常 |

## 性能指标
- 平均拦截延迟: XXXms
- 内存占用: XXXMB
- 点击成功率: XX%

## 建议
1. [根据测试结果填写]
```

## 🆘 获取帮助

1. 查看详细指南: `cat TESTING_OPENCLAW_INTEGRATION.md`
2. 运行兼容性测试: `python test_linux_compatibility.py`
3. 测试对话框系统: `python -c "from src.core.dialog import test_dialog_system; test_dialog_system()"`

---

**下一步**: 完成 macOS 测试后，将项目打包传输到 Linux 虚拟机进行实际 OpenClaw 集成测试。

**测试目标**: 验证 ClawShield 能正确拦截、评估和控制 OpenClaw 的点击命令，提供完整的安全防护。