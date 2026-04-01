# 🔌 OpenClaw 集成指南

本指南详细说明如何将 ClawShield 集成到 OpenClaw 中，为自动化点击操作提供实时安全防护。

## 📋 OpenClaw 简介

OpenClaw 是一个流行的开源自动化代理框架，用于执行 GUI 自动化任务，包括：
- 🖱️ 鼠标点击和移动
- ⌨️ 键盘输入和快捷键
- 📍 屏幕坐标定位
- 🔄 流程自动化和任务编排

**OpenClaw 典型命令格式**:
```bash
openclaw click 100 200
openclaw type "Hello World"
openclaw move 300 400
```

## 🛡️ ClawShield 集成模式

ClawShield 提供两种集成模式：

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| **包装器模式** | 在外部包装 OpenClaw 命令 | 快速集成，无需修改 OpenClaw 代码 |
| **插件/中间件模式** | 作为 OpenClaw 内部插件 | 深度集成，实时拦截所有点击 |

## 🚀 快速开始（包装器模式）

### 步骤 1: 安装 ClawShield
```bash
# 克隆仓库
git clone https://github.com/thefooliman/ClawShield.git
cd ClawShield

# 安装依赖
pip install -r requirements.txt

# 使 CLI 可执行
chmod +x clawshield
```

### 步骤 2: 测试集成
```bash
# 测试 OpenClaw 命令包装
./clawshield run --wrap openclaw "click 100 200"

# 输出示例:
# 🛡️ Wrapping OpenClaw command with ClawShield security...
# 📝 Command: click 100 200
# 🔍 Analyzing click at (100, 200)...
# ✅ Click executed safely
```

### 步骤 3: 替换 OpenClaw 调用
将原来的 OpenClaw 命令：
```bash
openclaw click 100 200
```

替换为：
```bash
./clawshield run --wrap openclaw "click 100 200"
```

或者创建别名：
```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias openclaw-secure="/path/to/ClawShield/clawshield run --wrap openclaw"

# 使用安全版本
openclaw-secure "click 100 200"
openclaw-secure "mouse click 300 400"
```

## 🔌 深度集成（插件模式）

### 步骤 1: 了解 OpenClaw 插件架构
OpenClaw 通常支持插件/中间件架构，允许在点击执行前后插入自定义逻辑。

**典型的 OpenClaw 插件接口**:
```python
class OpenClawPlugin:
    def before_click(self, x: int, y: int) -> bool:
        """在点击前调用，返回 True 允许点击，False 阻止点击"""
        pass

    def after_click(self, x: int, y: int, success: bool):
        """在点击后调用"""
        pass
```

### 步骤 2: 创建 OpenClaw 插件
ClawShield 已经提供了 `OpenClawMiddleware` 类，可以直接用作插件：

```python
# openclaw_plugin_clawshield.py
import sys
import os

# 添加 ClawShield 到路径
sys.path.insert(0, '/path/to/ClawShield')

from src.integration.openclaw_integration import OpenClawMiddleware

class ClawShieldOpenClawPlugin:
    """ClawShield OpenClaw 插件"""

    def __init__(self):
        self.middleware = OpenClawMiddleware()

    def before_click(self, x: int, y: int) -> bool:
        """点击前安全检查"""
        result = self.middleware.on_click(x, y, {
            'source': 'openclaw',
            'timestamp': time.time()
        })

        # 根据风险评估决定是否允许点击
        if result.get('risk_score', 0) > 0.7:
            print(f"🛑 High risk click blocked at ({x}, {y})")
            return False

        print(f"✅ Click allowed at ({x}, {y})")
        return True

    def after_click(self, x: int, y: int, success: bool):
        """点击后记录"""
        self.middleware.record_action(
            action='click',
            coordinates=(x, y),
            allowed=True,
            risk_score=0.5  # 实际应该从缓存中获取
        )

        if success:
            print(f"📝 Click recorded at ({x}, {y})")
```

### 步骤 3: 配置 OpenClaw 使用插件
根据 OpenClaw 的配置方式：

#### 方式 A: 配置文件
```yaml
# openclaw_config.yaml
plugins:
  - module: "openclaw_plugin_clawshield"
    class: "ClawShieldOpenClawPlugin"
    enabled: true
    config:
      log_level: "INFO"
      auto_block_high_risk: true
```

#### 方式 B: 命令行参数
```bash
openclaw --plugin openclaw_plugin_clawshield.ClawShieldOpenClawPlugin click 100 200
```

#### 方式 C: 代码集成
```python
# 在 OpenClaw 脚本中
import openclaw_plugin_clawshield

# 创建插件实例
clawshield_plugin = openclaw_plugin_clawshield.ClawShieldOpenClawPlugin()

# 注册到 OpenClaw
openclaw.register_plugin(clawshield_plugin)

# 执行命令
openclaw.execute("click 100 200")
```

## 📝 集成示例

### 示例 1: 自动化脚本集成
```python
#!/usr/bin/env python3
"""
安全自动化脚本示例
结合 OpenClaw 和 ClawShield
"""

import subprocess
import sys
import os

class SecureOpenClaw:
    def __init__(self, clawshield_path=None):
        self.clawshield_path = clawshield_path or "./clawshield"

    def safe_click(self, x, y, button="left"):
        """安全点击"""
        cmd = [self.clawshield_path, "run", "--wrap", "openclaw", "click", str(x), str(y)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            print(result.stdout)

            if result.returncode == 0:
                print(f"✅ Safe click executed at ({x}, {y})")
                return True
            else:
                print(f"❌ Click blocked or failed at ({x}, {y})")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ Click timeout at ({x}, {y})")
            return False

    def safe_type(self, text):
        """安全输入文本（直接传递给 OpenClaw）"""
        cmd = ["openclaw", "type", text]
        return subprocess.run(cmd, capture_output=True, text=True)

# 使用示例
if __name__ == "__main__":
    secure_oc = SecureOpenClaw()

    # 安全点击
    secure_oc.safe_click(100, 200)
    secure_oc.safe_click(300, 400)

    # 直接输入（无需安全评估）
    secure_oc.safe_type("Hello World")
```

### 示例 2: 批量任务处理
```python
"""
批量处理 OpenClaw 任务文件
"""

import json
import sys

def process_task_file(task_file, use_security=True):
    """处理 OpenClaw 任务文件"""

    with open(task_file, 'r') as f:
        tasks = json.load(f)

    for task in tasks:
        action = task.get('action')
        params = task.get('params', {})

        if action == 'click' and use_security:
            x = params.get('x')
            y = params.get('y')

            # 使用 ClawShield 包装器
            cmd = f"./clawshield run --wrap openclaw 'click {x} {y}'"
            print(f"🔒 Executing secure: {cmd}")

            # 执行命令...

        elif action == 'click' and not use_security:
            # 直接执行（无安全保护）
            cmd = f"openclaw click {params.get('x')} {params.get('y')}"
            print(f"⚠️ Executing without security: {cmd}")

        else:
            # 其他命令
            cmd = f"openclaw {action} {json.dumps(params)}"
            print(f"➡️ Executing: {cmd}")
```

## ⚙️ 配置选项

### ClawShield 包装器配置
```bash
# 设置日志级别
export CLAWSHIELD_LOG_LEVEL=DEBUG

# 设置风险阈值 (0.0-1.0)
export CLAWSHIELD_RISK_THRESHOLD=0.7

# 启用/禁用视觉 AI
export CLAWSHIELD_ENABLE_VISION=true

# Ollama 服务器地址
export OLLAMA_HOST=http://localhost:11434
```

### OpenClaw 集成配置
```python
# config.py
CLAWSHIELD_CONFIG = {
    'enabled': True,
    'mode': 'wrapper',  # 'wrapper' 或 'plugin'
    'risk_threshold': 0.7,
    'block_high_risk': True,
    'log_file': '/var/log/clawshield/openclaw.log',
    'cache_size': 1000,  # 历史记录缓存大小
}
```

## 🧪 测试集成

### 测试 1: 基本功能
```bash
# 测试点击命令包装
./clawshield run --wrap openclaw "click 100 200"

# 测试移动命令（应直接通过）
./clawshield run --wrap openclaw "move 300 400"

# 测试复杂命令
./clawshield run --wrap openclaw "mouse click --button right 500 600"
```

### 测试 2: 风险场景
```bash
# 模拟高风险点击（屏幕中心）
./clawshield run --wrap openclaw "click 960 540"

# 模拟安全点击（屏幕边缘）
./clawshield run --wrap openclaw "click 50 50"
```

### 测试 3: 性能测试
```bash
# 批量点击测试
for i in {1..10}; do
    ./clawshield run --wrap openclaw "click $((i*100)) $((i*50))"
done
```

## 🔍 故障排除

### 问题 1: OpenClaw 命令无法识别
**症状**: `intercepted_clicks: 0` 但命令包含点击
**解决**:
1. 检查命令格式：`click 100 200` 或 `mouse click 100 200`
2. 更新 `src/integration/openclaw_integration.py` 中的正则表达式
3. 使用 `--debug` 模式查看详细解析过程

### 问题 2: 插件加载失败
**症状**: OpenClaw 无法加载 ClawShield 插件
**解决**:
1. 确保 Python 路径正确
2. 检查插件类名和模块路径
3. 查看 OpenClaw 日志获取详细错误信息

### 问题 3: 性能问题
**症状**: 点击延迟过高
**解决**:
1. 禁用视觉 AI: `export CLAWSHIELD_ENABLE_VISION=false`
2. 增加缓存大小
3. 使用批处理模式

## 📊 监控和日志

### 查看执行日志
```bash
# 查看 ClawShield 日志
tail -f /var/log/clawshield/openclaw.log

# 详细调试信息
./clawshield run --wrap openclaw "click 100 200" --debug
```

### 监控指标
```bash
# 查看拦截统计
./clawshield stats

# 查看风险评估历史
./clawshield history
```

### 生成报告
```bash
# 生成安全报告
./clawshield report --format html --output security_report.html
```

## 🔄 持续集成

### GitHub Actions 示例
```yaml
name: Test OpenClaw Integration

on: [push, pull_request]

jobs:
  test-openclaw:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        sudo apt-get install -y tesseract-ocr

    - name: Test OpenClaw integration
      run: |
        python test_openclaw_integration_macos.py
        ./clawshield run --wrap openclaw "click 100 200"

    - name: Run security tests
      run: |
        python -m pytest tests/test_openclaw_integration.py
```

## 🚀 最佳实践

### 安全建议
1. **始终启用 ClawShield**：为所有 OpenClaw 任务启用安全防护
2. **定期更新**：保持 ClawShield 和 OpenClaw 最新版本
3. **监控日志**：定期检查安全日志和拦截记录
4. **测试高风险场景**：在生产前测试各种风险场景

### 性能优化
1. **批量处理**：将多个点击合并为单个安全评估批次
2. **缓存结果**：对重复坐标使用缓存的风险评估
3. **异步处理**：使用异步模式减少延迟
4. **选择性评估**：只为高风险区域启用完整评估

### 部署建议
1. **开发环境**：使用包装器模式快速集成
2. **测试环境**：同时测试包装器和插件模式
3. **生产环境**：使用插件模式确保实时防护
4. **监控环境**：启用详细日志和监控

## 📞 支持

### 获取帮助
1. **文档**: 查看 `TESTING_OPENCLAW_INTEGRATION.md` 和 `QUICK_START_OPENCLAW_TESTING.md`
2. **测试**: 运行 `python test_openclaw_integration_macos.py`
3. **示例**: 查看 `examples/openclaw_integration_example.py`

### 报告问题
```bash
# 收集调试信息
./clawshield diagnose --openclaw

# 提交 Issue
# 包括：OpenClaw 版本、错误日志、复现步骤
```

### 社区
- GitHub Issues: https://github.com/thefooliman/ClawShield/issues
- OpenClaw 社区: [OpenClaw 官方社区链接]

---

**下一步**: 根据你的 OpenClaw 版本和部署环境，选择合适的集成模式开始使用 ClawShield 安全防护。

**目标**: 确保所有 OpenClaw 自动化点击都经过实时安全评估，防止意外的高风险操作。