# VortiCrypt

[![VortiCrypt CI](https://github.com/aminmadaniofficial/VortiCrypt/actions/workflows/python-app.yml/badge.svg)](https://github.com/aminmadaniofficial/VortiCrypt/actions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)

**VortiCrypt** is an esoteric, highly visual 3D vector rotation cipher (3D-VRC) engine. It treats text characters as coordinate points $(x, y, z)$ inside a 3-dimensional Euclidean space $[0, 255]^3$ and encrypts them by applying sequential spatial rotations around the X, Y, and Z axes using dynamic, deterministically derived angles.

This repository features the complete cryptographic core, a command-line interface (CLI) for headless pipelines, and an interactive, real-time OpenGL-based desktop GUI (PyQt6 + PyQtGraph) that visualizes data scrambling as a dispersing particle constellation.

---

## 🛠️ Cryptographic Pipeline Architecture

### 1. Block Alignment & Padding (Block Size = 3 Bytes)
Since VortiCrypt operates in 3D coordinate space, the cipher block size is exactly 3 bytes (representing one $v = [x, y, z]^T$ point). To handle plaintext lengths that are not multiples of 3, a PKCS#7-like padding scheme is applied:
- Let $L$ be the byte length of the plaintext.
- The padding length is calculated as: $P = 3 - (L \pmod 3)$.
- $P$ bytes, each containing the byte value of $P$ itself, are appended to the payload.
- Upon decryption, the final byte of the restored byte stream dictates the quantity of padding bytes to discard.

### 2. Key Derivation Function (KDF)
The user-provided variable-length key is deterministically mapped to three rotation angles $(\theta_x, \theta_y, \theta_z)$ in degrees using prime scaling multipliers to limit linear correlation:
$$\text{hash\_val} = \sum_{i=0}^{N-1} (\text{ASCII}(key[i]) \times (i + 1))$$

The angles are calculated as:
$$\theta_x = (\text{hash\_val} \times 17) \pmod{360}$$
$$\theta_y = (\text{hash\_val} \times 31) \pmod{360}$$
$$\theta_z = (\text{hash\_val} \times 47) \pmod{360}$$

*Fallback:* If any calculated angle resolves to $0^\circ$, it is assigned a default fallback value ($\theta_x=45^\circ$, $\theta_y=90^\circ$, $\theta_z=135^\circ$) to guarantee spatial dispersion.

### 3. Encryption (Forward 3D Rotation)
For each 3-byte block represented as a vector $v = [x, y, z]^T$, the derived angles are converted to radians $(\alpha, \beta, \gamma)$. The encrypted state vector $v'$ is computed by applying sequential orthogonal rotation matrices:
$$v' = R_z(\gamma) \cdot R_y(\beta) \cdot R_x(\alpha) \cdot v$$

Where:
- **Rotation X ($R_x$):**
  $$R_x(\alpha) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\alpha & -\sin\alpha \\ 0 & \sin\alpha & \cos\alpha \end{bmatrix}$$
- **Rotation Y ($R_y$):**
  $$R_y(\beta) = \begin{bmatrix} \cos\beta & 0 & \sin\beta \\ 0 & 1 & 0 \\ -\sin\beta & 0 & \cos\beta \end{bmatrix}$$
- **Rotation Z ($R_z$):**
  $$R_z(\gamma) = \begin{bmatrix} \cos\gamma & -\sin\gamma & 0 \\ \sin\gamma & \cos\gamma & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

The resulting coordinates $v' = [x', y', z']^T$ are floating-point numbers representing the scrambled state in 3D space.

### 4. Decryption (Inverse 3D Rotation)
Because rotation matrices are orthogonal, their inverses are equal to their transposes ($R^{-1} = R^T$). To reverse the encryption path, VortiCrypt applies the transposed matrices in reverse sequential order:
$$v = R_x(\alpha)^T \cdot R_y(\beta)^T \cdot R_z(\gamma)^T \cdot v'$$

The reconstructed floating-point coordinates are rounded to the nearest integer to resolve floating-point drift:
$$[x, y, z] = [\text{round}(x), \text{round}(y), \text{round}(z)]$$
Boundary clipping is applied to ensure every coordinate maps securely back to the original $[0, 255]$ byte range before padding is stripped.

### 5. Binary Serialization
To store or transmit the floating-point coordinate tuples $[x', y', z']$ compactly, VortiCrypt scales the values by $1000$, packs them as 32-bit signed big-endian integers, and serializes the binary sequence into a standard Base64 string.

---

## 🚀 Features

- **Interactive 3D Visualizer:** An OpenGL-powered PyQtGraph canvas showing the byte coordinates inside a reference domain box, displaying real-time constellation connections.
- **Dynamic Transition Animations:** Visualizes the encryption step as a twisting helical dispersion of green (plaintext) particles into red (scrambled) particles.
- **Headless CLI Utility:** Perfect for pipeline operations, supporting file-based read/writes and raw standard input/output streams.
- **Dual-Pane UI:** Highly isolated modules for Encryption and Decryption with independent clipboard interactions and a dedicated mathematics reference panel.
- **Comprehensive Unit Testing:** Automated CI testing covering key derivation, padding, Base64 preservation, and Unicode integrity.

---

## 📦 Installation

To run VortiCrypt, clone the repository and install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/aminmadaniofficial/VortiCrypt.git
cd VortiCrypt

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest
```

---

## 💻 Usage

### 1. Graphical User Interface (GUI)
Launch the dark cyberpunk-themed 3D desktop application:
```bash
python -m vorticrypt.gui.app
```

### 2. Command-Line Interface (CLI)
Encrypt and decrypt data directly from the terminal.

* **Encryption Example:**
  ```bash
  python -m vorticrypt.cli -e -k "Nebula-9X" -m "Hello World"
  ```
  *Output:* A compact Base64 payload representing scaled spatial coordinates.

* **Decryption Example:**
  ```bash
  python -m vorticrypt.cli -d -k "Nebula-9X" -m "AABTNP/+UEYAAhoe..."
  ```

* **File Processing:**
  ```bash
  python -m vorticrypt.cli -e -k "MySecretKey" -i plaintext.txt -o encrypted.b64
  ```

---

## 🧪 Testing

Execute the test suite to verify cryptographic roundtrip consistency and boundary conditions:
```bash
python -m pytest tests/
```

---

## ⚠️ Cryptographic Analysis & Disclaimer

VortiCrypt is an **esoteric proof-of-concept** designed primarily for educational, visual, and research purposes. It is **not** a secure alternative to standard cryptographic primitives like AES or ChaCha20.

### Vulnerability Profile:
- **Linearity:** Because 3D spatial rotations are linear transformations, the cipher can be represented as a system of linear equations. It is highly susceptible to **Known-Plaintext Attacks (KPA)**. With a few known byte coordinates and their corresponding rotated coordinates, an attacker could resolve the transformation matrix using simple linear algebra (Gaussian elimination) without needing to brute-force the KDF.
- **Entropy & Diffusion:** While the cipher scatters coordinate points geometrically, the character-to-point mapping does not perform multi-round byte-substitution or active bit-level diffusion (like the S-Box layers in SPN ciphers).

Do not use VortiCrypt to secure highly confidential production data.

---

## 📄 License

This project is licensed under the terms of the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for more details.
