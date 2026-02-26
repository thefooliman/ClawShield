import sys
print("sys.path[0]:", sys.path[0])
print("Current working directory:", sys.path[0] if sys.path[0] else "empty")
print("Full sys.path:", sys.path)

try:
    from src.utils.coords import ScreenTransformer
    print("✅ Absolute import from src.utils.coords works")
except ImportError as e:
    print(f"❌ Absolute import failed: {e}")

# Try relative import
try:
    # This would only work if we're inside src package
    from .utils.coords import ScreenTransformer
    print("✅ Relative import works")
except ImportError as e:
    print(f"❌ Relative import failed: {e}")