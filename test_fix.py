#!/usr/bin/env python3
import sys
import os

print("=== 测试导入问题 ===")
print(f"当前目录: {os.getcwd()}")
print(f"sys.path: {sys.path}")

print("\n1. 测试直接从根目录导入:")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from src.utils.coords import ScreenTransformer
    print("✅ from src.utils.coords import ScreenTransformer - 成功")
except ImportError as e:
    print(f"❌ 失败: {e}")

print("\n2. 测试直接运行 src/main.py 的问题:")
print("当你在项目根目录运行: python src/main.py")
print("Python 的当前目录是项目根目录，但 src 可能不在 sys.path[0]")
print("当你在 src 目录运行: cd src && python main.py")
print("Python 的当前目录是 src，无法找到 'src' 包")

print("\n=== 解决方案 ===")
print("1. 在项目根目录运行，并使用 run.py 或添加 sys.path")
print("2. 或者使用: python -m src.main (从项目根目录)")
print("3. 或者修改 src/main.py 中的导入为相对导入: from .utils.coords import ScreenTransformer")

print("\n=== 测试使用 python -m ===")
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 确保在项目根目录
try:
    import subprocess
    result = subprocess.run([sys.executable, "-m", "src.main", "--help"],
                           capture_output=True, text=True, timeout=2)
    print("python -m src.main 执行成功")
except Exception as e:
    print(f"python -m src.main 可能失败: {e}")