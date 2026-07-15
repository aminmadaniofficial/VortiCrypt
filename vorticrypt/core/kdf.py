from typing import Tuple

class KeyDerivator:
    """Derives deterministic 3D rotation angles from user-defined text keys."""

    @staticmethod
    def derive_angles(key: str) -> Tuple[float, float, float]:
        """
        Derives angles in degrees. 
        Applies prime multipliers and falls back to standard values if 0.
        """
        if not key:
            raise ValueError("Cryptographic key cannot be empty.")

        # Hash calculation based on weighted position of character bytes
        hash_val = sum(ord(char) * (i + 1) for i, char in enumerate(key))

        # Scale using prime multipliers to guarantee non-linear dispersion
        tx = (hash_val * 17) % 360
        ty = (hash_val * 31) % 360
        tz = (hash_val * 47) % 360

        # Non-zero safe fallback values
        tx = tx if tx != 0 else 45
        ty = ty if ty != 0 else 90
        tz = tz if tz != 0 else 135

        return float(tx), float(ty), float(tz)