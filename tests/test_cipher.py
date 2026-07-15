# tests/test_cipher.py
import pytest
import base64
from vorticrypt.core.cipher import VortiCryptEngine
from vorticrypt.core.kdf import KeyDerivator
from vorticrypt.core.padding import BlockPadding

def test_deterministic_kdf():
    """Validates that the key derivation generates identical and stable outputs for the same keys."""
    key = "Nebula-9X"
    ax1, ay1, az1 = KeyDerivator.derive_angles(key)
    ax2, ay2, az2 = KeyDerivator.derive_angles(key)
    
    assert ax1 == ax2
    assert ay1 == ay2
    assert az1 == az2
    
    # Assert that different keys generate different angles
    ax3, ay3, az3 = KeyDerivator.derive_angles("Nebula-10X")
    assert (ax1, ay1, az1) != (ax3, ay3, az3)

def test_padding_and_unpadding():
    """Validates PKCS#7 block size rules for 3-byte configurations."""
    data_exact = b"ABC"  # Exactly divisible by 3
    padded_exact = BlockPadding.pad(data_exact)
    assert len(padded_exact) == 6  # Always adds padding
    assert BlockPadding.unpad(padded_exact) == data_exact

    data_partial = b"AB"  # 2 bytes
    padded_partial = BlockPadding.pad(data_partial)
    assert len(padded_partial) == 3
    assert BlockPadding.unpad(padded_partial) == data_partial

def test_unicode_lossless_roundtrip():
    """Tests that complex UTF-8 characters decrypt without precision drift."""
    payloads = [
        "Hello World",
        "رمزنگاری سه‌بعدی VortiCrypt 123",
        "⚡🛸 Cyberpunk aesthetic verification test! 🚀👽",
        "A" * 100,  # Large payload
        ""          # Empty payload
    ]
    key = "CyberSecretKey"
    cipher = VortiCryptEngine(key)

    for msg in payloads:
        vectors = cipher.encrypt(msg)
        decrypted = cipher.decrypt(vectors)
        assert decrypted == msg

def test_base64_serialization():
    """Ensures that serialization structures remain accurate down to floating-point scale limits."""
    key = "ScaleTest"
    cipher = VortiCryptEngine(key)
    message = "Data serialization validation."
    
    original_vectors = cipher.encrypt(message)
    b64_payload = cipher.serialize_b64(original_vectors)
    
    # Assert return payload is indeed valid base64
    assert base64.b64decode(b64_payload) is not None
    
    deserialized_vectors = cipher.deserialize_b64(b64_payload)
    
    # Check that vectors match within scaling epsilon limits (1/1000)
    for v1, v2 in zip(original_vectors, deserialized_vectors):
        assert abs(v1[0] - v2[0]) < 0.001
        assert abs(v1[1] - v2[1]) < 0.001
        assert abs(v1[2] - v2[2]) < 0.001

def test_tampered_payload_decryption():
    """Ensures incorrect structures or altered payloads throw safe errors."""
    cipher = VortiCryptEngine("SecureKey")
    malformed_b64 = "YW55IGNhcm5hbCBwbGVhc3VyZS4=" # Random base64 string
    
    with pytest.raises(Exception):
        vectors = cipher.deserialize_b64(malformed_b64)
        # Should fail to unpad correctly due to randomized byte configurations
        cipher.decrypt(vectors)