import numpy as np
from PyQt6.QtCore import QTimer
import pyqtgraph.opengl as gl
from typing import List, Tuple

class Cyber3DCanvas(gl.GLViewWidget):
    """OpenGL based 3D canvas showing real-time vector transformations with spatial grids."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCameraPosition(distance=340, elevation=22, azimuth=45)
        
        # Add 3D Colored Axes (Red: X, Green: Y, Blue: Z)
        axes = gl.GLAxisItem()
        axes.setSize(160, 160, 160)
        self.addItem(axes)

        # Draw Byte Domain Cage
        self._create_boundary_cube()

        # Scatter plot for points (Particles)
        self.scatter = gl.GLScatterPlotItem()
        self.addItem(self.scatter)

        # Line plot for connections (Constellation/Data-trails)
        self.lines = gl.GLLinePlotItem()
        self.addItem(self.lines)

        # Passive idle rotation timer
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self._idle_rotate)
        self.idle_timer.start(30)

        # Animation states
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._animation_step)
        
        self.start_points: np.ndarray = np.empty((0, 3))
        self.end_points: np.ndarray = np.empty((0, 3))
        self.current_points: np.ndarray = np.empty((0, 3))
        self.colors: np.ndarray = np.empty((0, 4))
        
        self.animation_step = 0
        self.total_steps = 80  # Number of frames
        self.is_animating = False

    def _create_boundary_cube(self):
        """Draws a holographic wireframe box enclosing the 0-255 byte domain."""
        cube_edges = np.array([
            [0,0,0], [255,0,0], [255,0,0], [255,255,0], [255,255,0], [0,255,0], [0,255,0], [0,0,0],
            [0,0,255], [255,0,255], [255,0,255], [255,255,255], [255,255,255], [0,255,255], [0,255,255], [0,0,255],
            [0,0,0], [0,0,255], [255,0,0], [255,0,255], [255,255,0], [255,255,255], [0,255,0], [0,255,255]
        ], dtype=float)
        
        # Center the cube around the coordinate origin
        cube_edges -= 127.5

        cube_lines = gl.GLLinePlotItem(
            pos=cube_edges,
            color=(0, 255, 204, 30),  # Transparent teal
            width=1.0,
            mode='lines'
        )
        self.addItem(cube_lines)

    def _idle_rotate(self):
        """Applies a continuous subtle rotation to the camera when idle."""
        if not self.is_animating:
            self.opts['azimuth'] = (self.opts['azimuth'] + 0.12) % 360
            self.update()

    def render_live_state(self, points: List[Tuple[float, float, float]], is_encrypted: bool = False):
        """Renders static points instantly (used for real-time text-change preview)."""
        if self.is_animating or not points:
            return
            
        pts = np.array(points) - 127.5
        
        colors = np.zeros((len(points), 4))
        if is_encrypted:
            colors[:, 0] = 1.0  # Cyberpunk Red
            colors[:, 3] = 0.9
        else:
            colors[:, 1] = 1.0  # Holographic Green
            colors[:, 3] = 0.8

        self.scatter.setData(pos=pts, color=colors, size=8)
        self.lines.setData(pos=pts, color=(0, 255, 204, 90) if not is_encrypted else (255, 0, 85, 90), width=1.5, mode='line_strip')

    def trigger_transition(self, start: List[Tuple[float, float, float]], end: List[Tuple[float, float, float]], decrypt_mode: bool = False):
        """Initiates a smooth animated transition between decrypted/encrypted layouts."""
        if not start or not end:
            return
            
        self.start_points = np.array(start) - 127.5
        self.end_points = np.array(end) - 127.5
        self.current_points = np.copy(self.start_points)
        self.is_animating = True
        self.decrypt_mode = decrypt_mode
        
        self.colors = np.zeros((len(start), 4))
        if self.decrypt_mode:
            self.colors[:, 0] = 1.0  # Start Red
        else:
            self.colors[:, 1] = 1.0  # Start Green
        self.colors[:, 3] = 0.8

        self.animation_step = 0
        self.anim_timer.start(16)  # ~60 FPS

    def _animation_step(self):
        """Processes a frame of interpolation and rotational dispersion."""
        if self.animation_step >= self.total_steps:
            self.anim_timer.stop()
            self.is_animating = False
            return

        self.animation_step += 1
        t = self.animation_step / self.total_steps
        
        # S-curve interpolation
        ease_t = (1.0 - np.cos(t * np.pi)) / 2.0

        # Linear coordinate interpolation combined with extra helical rotation for flair
        self.current_points = self.start_points + (self.end_points - self.start_points) * ease_t
        
        # Helical spin effect
        spin_angle = np.sin(t * np.pi) * 0.25
        cos_s, sin_s = np.cos(spin_angle), np.sin(spin_angle)
        xs = self.current_points[:, 0] * cos_s - self.current_points[:, 1] * sin_s
        ys = self.current_points[:, 0] * sin_s + self.current_points[:, 1] * cos_s
        self.current_points[:, 0] = xs
        self.current_points[:, 1] = ys

        # Color transformation
        if self.decrypt_mode:
            self.colors[:, 0] = 1.0 - ease_t  # Red fades out
            self.colors[:, 1] = ease_t        # Green fades in
        else:
            self.colors[:, 0] = ease_t        # Red fades in
            self.colors[:, 1] = 1.0 - ease_t  # Green fades out
            
        self.colors[:, 2] = ease_t * 0.4
        self.colors[:, 3] = 0.8

        self.scatter.setData(pos=self.current_points, color=self.colors)
        self.lines.setData(pos=self.current_points, color=self.colors, width=1.5, mode='line_strip')
        
        # Dynamic rotation of camera to emphasize spatial scrambling
        self.opts['azimuth'] = (self.opts['azimuth'] + 0.3) % 360