import math
import struct
import base64
from typing import List, Tuple
from vorticrypt.core.padding import BlockPadding
from vorticrypt.core.kdf import KeyDerivator
from vorticrypt.utils.math_helpers import rotate_x, rotate_y, rotate_z

class VortiCryptEngine:
    """Core cryptographic engine responsible for vector rotations and Base64 serialization."""

    def __init__(self, key: str):
        self.theta_x, self.theta_y, self.theta_z = KeyDerivator.derive_angles(key)

    def forward_rotation(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Applies sequential Rz * Ry * Rx rotation."""
        rx = math.radians(self.theta_x)
        ry = math.radians(self.theta_y)
        rz = math.radians(self.theta_z)

        x1, y1, z1 = rotate_x(x, y, z, rx)
        x2, y2, z2 = rotate_y(x1, y1, z1, ry)
        x3, y3, z3 = rotate_z(x2, y2, z2, rz)
        return x3, y3, z3

    def inverse_rotation(self, x3: float, y3: float, z3: float) -> Tuple[float, float, float]:
        """Applies inverse rotations in reverse sequence (Rx_inv * Ry_inv * Rz_inv)."""
        rx = math.radians(self.theta_x)
        ry = math.radians(self.theta_y)
        rz = math.radians(self.theta_z)

        x2, y2, z2 = rotate_z(x3, y3, z3, -rz)
        x1, y1, z1 = rotate_y(x2, y2, z2, -ry)
        x, y, z = rotate_x(x1, y1, z1, -rx)
        return x, y, z

    def encrypt(self, plaintext: str) -> List[Tuple[float, float, float]]:
        """Encrypts UTF-8 plaintext into a series of rotated 3D spatial points."""
        data = plaintext.encode("utf-8")
        padded_data = BlockPadding.pad(data)
        vectors = []

        for i in range(0, len(padded_data), 3):
            vx = float(padded_data[i])
            vy = float(padded_data[i+1])
            vz = float(padded_data[i+2])
            vectors.append(self.forward_rotation(vx, vy, vz))

        return vectors

    def decrypt(self, vectors: List[Tuple[float, float, float]]) -> str:
        """Decrypts 3D spatial points back into unpadded UTF-8 plaintext."""
        decrypted_bytes = bytearray()

        for vec in vectors:
            rx, ry, rz = self.inverse_rotation(vec[0], vec[1], vec[2])
            
            # Reconstruction via rounding to clear float-drift
            x_val = max(0, min(255, int(round(rx))))
            y_val = max(0, min(255, int(round(ry))))
            z_val = max(0, min(255, int(round(rz))))
            
            decrypted_bytes.extend([x_val, y_val, z_val])

        unpadded = BlockPadding.unpad(bytes(decrypted_bytes))
        return unpadded.decode("utf-8")

    def serialize_b64(self, vectors: List[Tuple[float, float, float]]) -> str:
        """Serializes 3D float vectors using high precision scaling into Base64."""
        binary_payload = bytearray()
        for x, y, z in vectors:
            scaled_x = int(round(x * 1000))
            scaled_y = int(round(y * 1000))
            scaled_z = int(round(z * 1000))
            binary_payload.extend(struct.pack(">iii", scaled_x, scaled_y, scaled_z))
            
        return base64.b64encode(binary_payload).decode("utf-8")

    def deserialize_b64(self, b64_str: str) -> List[Tuple[float, float, float]]:
        """Deserializes Base64 payload back into float vectors."""
        binary_data = base64.b64decode(b64_str)
        vectors = []
        element_size = 12
        
        for i in range(0, len(binary_data), element_size):
            chunk = binary_data[i:i+element_size]
            if len(chunk) < element_size:
                break
            scaled_x, scaled_y, scaled_z = struct.unpack(">iii", chunk)
            vectors.append((scaled_x / 1000.0, scaled_y / 1000.0, scaled_z / 1000.0))
            
        return vectors