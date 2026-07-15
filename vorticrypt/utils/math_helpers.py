import math
from typing import Tuple

def rotate_x(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    """Applies rotation around the X-axis."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return x, y * cos_a - z * sin_a, y * sin_a + z * cos_a

def rotate_y(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    """Applies rotation around the Y-axis."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a

def rotate_z(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    """Applies rotation around the Z-axis."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a, z