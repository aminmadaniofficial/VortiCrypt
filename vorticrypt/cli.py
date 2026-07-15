import argparse
import sys
from vorticrypt.core.cipher import VortiCryptEngine

def main():
    """
    VortiCrypt Command Line Interface.
    Allows pipeline encryption and decryption of texts with custom file logging.
    """
    parser = argparse.ArgumentParser(
        description="VortiCrypt: A 3D Vector Rotation Cipher Command Line Interface.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", action="store_true", help="Run in encryption mode.")
    group.add_argument("-d", "--decrypt", action="store_true", help="Run in decryption mode.")

    parser.add_argument("-k", "--key", required=True, type=str, help="Cryptographic key for the KDF.")
    parser.add_argument("-m", "--message", type=str, help="Plaintext message or Base64 payload string.")
    parser.add_argument("-i", "--input-file", type=str, help="Path to input file containing target data.")
    parser.add_argument("-o", "--output-file", type=str, help="Path to output file where results are written.")

    args = parser.parse_args()

    # Determine input source
    data = ""
    if args.message:
        data = args.message
    elif args.input_file:
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                data = f.read().strip()
        except Exception as e:
            print(f"[-] Error reading file: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[-] Error: You must supply either a message string (-m) or an input file (-i).", file=sys.stderr)
        sys.exit(1)

    try:
        cipher = VortiCryptEngine(args.key)
        result = ""

        if args.encrypt:
            # Perform encryption & serialize to Base64
            vectors = cipher.encrypt(data)
            result = cipher.serialize_b64(vectors)
        elif args.decrypt:
            # Deserialize from Base64 & perform decryption
            vectors = cipher.deserialize_b64(data)
            result = cipher.decrypt(vectors)

        # Output results
        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"[+] Operational success. Output logged to '{args.output_file}'")
        else:
            print(result)

    except Exception as e:
        print(f"[-] Cryptographic operation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()