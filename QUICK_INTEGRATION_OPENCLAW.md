# 🚀 OpenClaw 快速集成指南

## 📋 前提条件

1. **OpenClaw** 已安装并可以正常运行
   ```bash
   openclaw --version
   ```

2. **ClawShield** 已安装
   ```bash
   git clone https://github.com/thefooliman/ClawShield.git
   cd ClawShield
   pip install -r requirements.txt
   chmod +x clawshield
   ```

## 🔧 集成方法选择

### 方法 A: 命令行包装器（最简单）
✅ **适合**: 快速测试、简单脚本、临时使用
```bash
# 将原来的 OpenClaw 命令:
openclaw click 100 200

# 替换为:
./clawshield run --wrap openclaw "click 100 200"
```

### 方法 B: 插件模式（最强大）
✅ **适合**: 生产环境、复杂自动化、需要实时防护
```python
# 在你的 OpenClaw 脚本中导入插件
from openclaw_plugin_clawshield import ClawShieldOpenClawPlugin

plugin = ClawShieldOpenClawPlugin(config={...})
```

### 方法 C: 混合模式（推荐）
✅ **适合**: 大多数实际场景，平衡简单性和功能性

## 🚀 5分钟快速集成

### 步骤 1: 测试基本功能
```bash
# 测试 ClawShield 是否工作
python test_openclaw_integration_macos.py

# 测试包装器模式
./clawshield run --wrap openclaw "click 100 200"
```

### 步骤 2: 创建别名（可选）
```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias secure-click="/path/to/ClawShield/clawshield run --wrap openclaw"

# 使用别名
secure-click "click 100 200"
secure-click "mouse click 300 400"
```

### 步骤 3: 修改现有脚本
找到你的 OpenClaw 脚本，将 `openclaw` 命令替换为安全版本：

**修改前** (`automation.sh`):
```bash
#!/bin/bash
openclaw click 100 200
openclaw type "Hello"
openclaw click 300 400
```

**修改后** (`secure_automation.sh`):
```bash
#!/bin/bash
/path/to/ClawShield/clawshield run --wrap openclaw "click 100 200"
openclaw type "Hello"  # 非点击命令可以直接使用
/path/to/ClawShield/clawshield run --wrap openclaw "click 300 400"
```

## 🔌 高级插件集成

### 步骤 1: 安装插件
```bash
# 复制插件文件到 OpenClaw 插件目录
cp examples/openclaw_plugin_clawshield.py ~/.openclaw/plugins/

# 或者复制到项目目录
cp examples/openclaw_plugin_clawshield.py /path/to/your/project/
```

### 步骤 2: 配置 OpenClaw
创建配置文件 `openclaw_config_secure.yaml`:
```yaml
plugins:
  - name: "clawshield"
    module: "openclaw_plugin_clawshield"
    class: "ClawShieldOpenClawPlugin"
    enabled: true
    config:
      log_level: "INFO"
      auto_block_high_risk: true
```

### 步骤 3: 运行安全自动化
```bash
# 使用配置文件
openclaw --config openclaw_config_secure.yaml run your_automation_task

# 或者在代码中
import openclaw

# 加载配置
openclaw.load_config("openclaw_config_secure.yaml")

# 执行任务
openclaw.run("your_automation_task")
```

## 🧪 测试集成

### 测试 1: 基本功能
```bash
# 测试安全点击
./clawshield run --wrap openclaw "click 100 200"

# 测试移动命令（应该直接通过）
./clawshield run --wrap openclaw "move 300 400"

# 查看执行结果
# 应该看到: "🔍 Analyzing click at (100, 200)..." 等日志
```

### 测试 2: 高风险场景
```bash
# 测试屏幕中心点击（高风险）
./clawshield run --wrap openclaw "click 960 540"

# 应该看到警告或用户确认对话框
```

### 测试 3: 批量测试
```bash
# 创建测试脚本
cat > test_clicks.sh << 'EOF'
#!/bin/bash
for i in {1..5}; do
  ./clawshield run --wrap openclaw "click $((i*100)) $((i*100))"
  sleep 0.5
done
EOF

chmod +x test_clicks.sh
./test_clicks.sh
```

## 📊 监控和调试

### 查看日志
```bash
# 启用详细日志
export CLAWSHIELD_LOG_LEVEL=DEBUG

# 运行命令并查看输出
./clawshield run --wrap openclaw "click 100 200" --debug
```

### 获取统计信息
```bash
# 查看安全统计
./clawshield stats

# 查看风险评估历史
./clawshield history
```

### 调试插件
```python
# 直接测试插件
python examples/openclaw_plugin_clawshield.py --test-click 100 200
python examples/openclaw_plugin_clawshield.py --stats
```

## 🔧 故障排除

### 问题 1: "No module named 'integration'"
```bash
# 确保在 ClawShield 项目根目录运行
cd /path/to/ClawShield

# 清理 Python 缓存
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
```

### 问题 2: OpenClaw 命令无法识别
```bash
# 检查命令格式
./clawshield run --wrap openclaw "click 100 200"  # 正确
./clawshield run --wrap openclaw click 100 200    # 也正确

# 如果使用复杂格式，可能需要更新解析器
# 编辑: src/integration/openclaw_integration.py
# 修改 _extract_clicks() 方法中的正则表达式
```

### 问题 3: 性能问题
```bash
# 禁用视觉 AI（加快速度）
export CLAWSHIELD_ENABLE_VISION=false

# 减少截图区域大小
export CLAWSHIELD_SCREENSHOT_SIZE=100

# 使用缓存
export CLAWSHIELD_ENABLE_CACHE=true
```

## 📝 最佳实践

### 安全实践
1. **始终启用 ClawShield**：为所有生产环境自动化启用
2. **定期更新**：保持 ClawShield 最新
3. **监控日志**：定期检查安全日志
4. **测试高风险场景**：在生产前测试各种情况

### 性能优化
1. **批量处理**：合并多个点击为单个安全评估
2. **缓存评估结果**：对重复坐标使用缓存
3. **选择性评估**：只为高风险区域启用完整评估
4. **异步处理**：使用异步模式减少延迟

### 部署建议
- **开发环境**：使用命令行包装器快速测试
- **测试环境**：同时测试包装器和插件模式
- **生产环境**：使用插件模式确保实时防护

## 🚀 生产环境部署

### Docker 集成
```dockerfile
FROM python:3.12

# 安装 OpenClaw 和 ClawShield
RUN pip install openclaw
COPY ClawShield /app/ClawShield

# 设置环境变量
ENV CLAWSHIELD_ENABLED=true
ENV CLAWSHIELD_MODE=plugin

# 启动脚本
CMD ["python", "/app/automation.py"]
```

### CI/CD 集成
```yaml
# GitHub Actions 示例
name: Secure Automation
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install ClawShield
        run: |
          pip install -r ClawShield/requirements.txt

      - name: Run secure automation
        run: |
          ClawShield/clawshield run --wrap openclaw "click 100 200"
```

## 📞 获取帮助

### 文档
- `INTEGRATION_GUIDE_OPENCLAW.md` - 详细集成指南
- `TESTING_OPENCLAW_INTEGRATION.md` - 测试指南
- `examples/` - 示例代码和配置

### 测试
```bash
# 运行完整测试套件
python test_openclaw_integration_macos.py

# 运行集成示例
python examples/integration_example.py
```

### 报告问题
```bash
# 收集诊断信息
./clawshield diagnose --openclaw

# 包括以下信息报告问题:
# 1. OpenClaw 版本
# 2. 错误日志
# 3. 复现步骤
# 4. 环境信息
```

---

**下一步**: 根据你的需求选择合适的集成方法，开始为你的 OpenClaw 自动化添加安全防护！

**目标**: 确保所有自动化点击都经过实时风险评估，防止意外的高风险操作。