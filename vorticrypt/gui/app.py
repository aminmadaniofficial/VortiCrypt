import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSplitter, QGroupBox, QTabWidget
)
from PyQt6.QtCore import Qt
from vorticrypt.core.cipher import VortiCryptEngine
from vorticrypt.core.padding import BlockPadding
from vorticrypt.gui.canvas_3d import Cyber3DCanvas


class VortiCryptApp(QMainWindow):
    """
    Main Application Window splitting Encryption and Decryption pipelines into Tabs,
    providing live previews, telemetry outputs, and an informational dashboard.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VortiCrypt // 3D Vector Rotation Cipher Engine")
        self.resize(1280, 780)
        
        self.setup_ui()
        self.apply_cyber_styling()
        
        # Trigger initial preview mapping
        self.handle_live_preview()

    def setup_ui(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        # ==========================================
        # LEFT PANEL: TABS & SYSTEM CONTROLS
        # ==========================================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # Global Cipher Key Widget (Sticky at the top)
        key_group = QGroupBox("CRYPTOGRAPHIC KEY (SHARED SECRET)")
        key_group_layout = QVBoxLayout(key_group)
        self.key_input = QLineEdit("Nebula-9X")
        self.key_input.textChanged.connect(lambda: self.handle_live_preview())
        key_group_layout.addWidget(self.key_input)
        left_layout.addWidget(key_group)

        # System Tabs
        self.tabs = QTabWidget()
        
        # Initialize tabs
        self.encrypt_tab = QWidget()
        self.decrypt_tab = QWidget()
        self.info_tab = QWidget()
        
        self.tabs.addTab(self.encrypt_tab, "  ENCRYPT MODULE  ")
        self.tabs.addTab(self.decrypt_tab, "  DECRYPT MODULE  ")
        self.tabs.addTab(self.info_tab, "  ALGORITHM INFO  ")
        
        left_layout.addWidget(self.tabs)

        # Populate Tabs
        self._build_encrypt_tab()
        self._build_decrypt_tab()
        self._build_info_tab()

        # ==========================================
        # RIGHT PANEL: VISUALIZER & COORDS
        # ==========================================
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # 3D Visualizer Canvas
        self.canvas_3d = Cyber3DCanvas()
        right_layout.addWidget(self.canvas_3d, stretch=8)

        # Technical Telemetry Panel
        telemetry_group = QGroupBox("REAL-TIME SPATIAL TELEMETRY")
        telemetry_layout = QVBoxLayout(telemetry_group)
        self.telemetry_output = QTextEdit()
        self.telemetry_output.setReadOnly(True)
        self.telemetry_output.setMaximumHeight(110)
        telemetry_layout.addWidget(self.telemetry_output)
        right_layout.addWidget(telemetry_group, stretch=2)

        # Bind Splitter panels
        main_splitter.addWidget(left_container)
        main_splitter.addWidget(right_container)
        main_splitter.setSizes([500, 780])

        self.last_encrypted_vectors = []

    def _build_encrypt_tab(self):
        layout = QVBoxLayout(self.encrypt_tab)
        layout.setContentsMargins(10, 15, 10, 10)

        layout.addWidget(QLabel("PLAINTEXT MESSAGE:"))
        self.plain_input = QTextEdit("Visual cryptography with 3D-VRC is elegant!")
        self.plain_input.textChanged.connect(self.handle_live_preview)
        layout.addWidget(self.plain_input)

        self.encrypt_btn = QPushButton("ENCRYPT AND ROTATE VECTORS")
        self.encrypt_btn.clicked.connect(self.handle_encryption)
        layout.addWidget(self.encrypt_btn)

        layout.addWidget(QLabel("CIPHERTEXT OUTPUT (BASE64 SERIALIZED):"))
        self.encrypt_b64_output = QTextEdit()
        self.encrypt_b64_output.setReadOnly(True)
        layout.addWidget(self.encrypt_b64_output)

    def _build_decrypt_tab(self):
        layout = QVBoxLayout(self.decrypt_tab)
        layout.setContentsMargins(10, 15, 10, 10)

        layout.addWidget(QLabel("CIPHERTEXT INPUT (BASE64 SERIALIZED):"))
        self.decrypt_b64_input = QTextEdit()
        layout.addWidget(self.decrypt_b64_input)

        self.decrypt_btn = QPushButton("REVERSE ROTATION AND DECRYPT")
        self.decrypt_btn.clicked.connect(self.handle_decryption)
        layout.addWidget(self.decrypt_btn)

        layout.addWidget(QLabel("RECONSTRUCTED PLAINTEXT MESSAGE:"))
        self.decrypt_plain_output = QTextEdit()
        self.decrypt_plain_output.setReadOnly(True)
        layout.addWidget(self.decrypt_plain_output)

    def _build_info_tab(self):
        """Displays formatted specification sheets of VortiCrypt algorithm."""
        layout = QVBoxLayout(self.info_tab)
        layout.setContentsMargins(10, 15, 10, 10)

        info_box = QTextEdit()
        info_box.setReadOnly(True)
        info_box.setHtml("""
            <h3>VORTICRYPT (3D-VRC) SPECIFICATION</h3>
            <p>VortiCrypt maps characters onto 3-dimensional coordinate vectors and scrambles them through mathematical matrices.</p>
            
            <h4>1. Mathematical Foundations</h4>
            <p>A message is divided into blocks of 3 bytes representing coordinate vector <b>v = [x, y, z]<sup>T</sup></b> where <i>x, y, z &isin; [0, 255]</i>.</p>
            <p>Rotation transforms coordinates sequentially across X, Y, and Z axes using angles derived from the shared key:</p>
            <p style='color:#00ffcc;'><b>v' = R<sub>z</sub>(&theta;<sub>z</sub>) &middot; R<sub>y</sub>(&theta;<sub>y</sub>) &middot; R<sub>x</sub>(&theta;<sub>x</sub>) &middot; v</b></p>
            
            <h4>2. Key Derivation Function (KDF)</h4>
            <p>Angles are computed deterministically using character positions and scaling with prime numbers to avoid linear dependency:</p>
            <ul>
                <li>&theta;<sub>x</sub> = (hash &times; 17) mod 360</li>
                <li>&theta;<sub>y</sub> = (hash &times; 31) mod 360</li>
                <li>&theta;<sub>z</sub> = (hash &times; 47) mod 360</li>
            </ul>

            <h4>3. Lossless Decryption</h4>
            <p>To reconstruct the data without floating-point degradation, we apply transpose (inverse) rotation matrices in reverse order:</p>
            <p style='color:#ff0055;'><b>v = R<sub>x</sub>(&theta;<sub>x</sub>)<sup>T</sup> &middot; R<sub>y</sub>(&theta;<sub>y</sub>)<sup>T</sup> &middot; R<sub>z</sub>(&theta;<sub>z</sub>)<sup>T</sup> &middot; v'</b></p>
            <p>Each value is then rounded to the nearest integer to restore original bytes.</p>
        """)
        layout.addWidget(info_box)

    def get_raw_points_from_plaintext(self, text: str) -> List[Tuple[float, float, float]]:
        """Maps plaintext string to unencrypted 3D points in [0, 255] space."""
        raw_bytes = BlockPadding.pad(text.encode("utf-8"))
        points = []
        for i in range(0, len(raw_bytes), 3):
            points.append((float(raw_bytes[i]), float(raw_bytes[i+1]), float(raw_bytes[i+2])))
        return points

    def handle_live_preview(self):
        """Generates dynamic live updates on the 3D canvas when typing."""
        text = self.plain_input.toPlainText()
        if not text:
            self.canvas_3d.render_live_state([])
            self.telemetry_output.clear()
            return

        points = self.get_raw_points_from_plaintext(text)
        self.canvas_3d.render_live_state(points, is_encrypted=False)
        
        coords_str = ", ".join([f"({p[0]:.0f}, {p[1]:.0f}, {p[2]:.0f})" for p in points])
        self.telemetry_output.setPlainText(f"Plain Points [0-255 Byte Space]:\n{coords_str}")

    def handle_encryption(self):
        key = self.key_input.text()
        text = self.plain_input.toPlainText()
        if not key or not text:
            return

        cipher = VortiCryptEngine(key)
        self.last_encrypted_vectors = cipher.encrypt(text)

        # Visual transition
        start_points = self.get_raw_points_from_plaintext(text)
        self.canvas_3d.trigger_transition(start_points, self.last_encrypted_vectors, decrypt_mode=False)

        # Output Base64
        serialized_b64 = cipher.serialize_b64(self.last_encrypted_vectors)
        self.encrypt_b64_output.setPlainText(serialized_b64)

        # Copy to decryption input automatically for premium UX
        self.decrypt_b64_input.setPlainText(serialized_b64)

        # Telemetry
        coords_str = "\n".join([f"[{v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f}]" for v in self.last_encrypted_vectors])
        self.telemetry_output.setPlainText(f"Encrypted Spatial Vectors:\n{coords_str}")

    def handle_decryption(self):
        key = self.key_input.text()
        b64_data = self.decrypt_b64_input.toPlainText().strip()
        if not key or not b64_data:
            return

        try:
            cipher = VortiCryptEngine(key)
            vectors = cipher.deserialize_b64(b64_data)
            
            # Decrypt back to string
            decrypted_text = cipher.decrypt(vectors)
            self.decrypt_plain_output.setPlainText(decrypted_text)

            # Reconstruct original points for animation
            target_points = self.get_raw_points_from_plaintext(decrypted_text)
            
            # Smooth reverse rotation animation (Red to Green transition)
            self.canvas_3d.trigger_transition(vectors, target_points, decrypt_mode=True)
            
            self.telemetry_output.setPlainText("Inverse rotation matrix resolved correctly. Reconstructed byte streams.")
        except Exception as e:
            self.decrypt_plain_output.setPlainText(f"Reconstruction Failure: {str(e)}")

    def apply_cyber_styling(self):
        """Cyberpunk stylesheet configuration using clean system typography."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0e14;
            }
            QWidget {
                background-color: #0b0e14;
                color: #00ffcc;
                font-family: 'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #1c273a;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
                color: #ff0055;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #1c273a;
                border-radius: 4px;
                background-color: #0d121c;
            }
            QTabBar::tab {
                background-color: #080a0f;
                border: 1px solid #1c273a;
                padding: 8px 16px;
                color: #8fa0b5;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0d121c;
                border-bottom-color: #0d121c;
                color: #00ffcc;
                font-weight: bold;
            }
            QLabel {
                font-weight: bold;
                color: #00ffcc;
                margin-top: 5px;
            }
            QLineEdit, QTextEdit {
                background-color: #070a0f;
                border: 1px solid #1c273a;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #ff0055;
            }
            QPushButton {
                background-color: #120317;
                border: 1px solid #ff0055;
                color: #ff0055;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
                margin-top: 6px;
                margin-bottom: 6px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #ff0055;
                color: #0b0e14;
            }
            QSplitter::handle {
                background-color: #111622;
            }
        """)

def main():
    import os
    os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
    os.environ["MESA_DEBUG"] = "silent"
    os.environ["QSG_RHI_BACKEND"] = "opengl"
    
    app = QApplication(sys.argv)
    window = VortiCryptApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()