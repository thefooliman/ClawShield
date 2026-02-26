import numpy as np
from AppKit import NSScreen

class ScreenTransformer:
    def __init__(self):
        # Core logic: Get scaling ratio between physical pixels and logical points on Mac system
        # Typically Retina displays return 2.0, newer models may be 3.0
        self.scale = NSScreen.mainScreen().backingScaleFactor()
        
        # Linear transformation matrix: Screen_Physical = Matrix * Input_Logic
        self.matrix = np.diag([self.scale, self.scale])
        print(f"📡 Coordinate engine initialized: Detected Retina scaling factor is {self.scale}")

    def to_physical(self, logic_x, logic_y):
        """Convert logical coordinates from pyautogui to real screen physical pixel coordinates"""
        logic_vec = np.array([logic_x, logic_y])
        phys_vec = np.dot(self.matrix, logic_vec)
        return phys_vec.astype(int)

    def to_logic(self, phys_x, phys_y):
        """Restore physical pixel coordinates to logical coordinates"""
        phys_vec = np.array([phys_x, phys_y])
        # Use inverse matrix for restoration (classic linear algebra application)
        inv_matrix = np.linalg.inv(self.matrix)
        logic_vec = np.dot(inv_matrix, phys_vec)
        return logic_vec.astype(int)

# Test code
if __name__ == "__main__":
    st = ScreenTransformer()
    test_pt = (100, 100)
    print(f"Logical point {test_pt} -> Physical pixels {st.to_physical(*test_pt)}")