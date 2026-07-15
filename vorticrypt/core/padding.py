class BlockPadding:
    """Handles PKCS#7-like padding scaled to 3-byte blocks."""
    
    BLOCK_SIZE = 3

    @classmethod
    def pad(cls, data: bytes) -> bytes:
        """Pads the byte sequence to be a multiple of BLOCK_SIZE."""
        pad_len = cls.BLOCK_SIZE - (len(data) % cls.BLOCK_SIZE)
        padding = bytes([pad_len] * pad_len)
        return data + padding

    @classmethod
    def unpad(cls, data: bytes) -> bytes:
        """Removes padding safely from the decrypted byte sequence."""
        if not data:
            return b""
        pad_len = data[-1]
        if pad_len < 1 or pad_len > cls.BLOCK_SIZE:
            raise ValueError("Invalid padding layout.")
        return data[:-pad_len]