"""Main application window."""

import sys
import os
import ctypes
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QTimer, QPointF, pyqtSignal, QSize, QThread, QMutex, QMutexLocker
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QImage, QPainter

from src.gui.chat_panel import ChatPanel
from src.gui.settings_dialog import SettingsDialog
from src.gui.widgets import AnimationTimeline, HUDControlOverlay
from src.manim_bridge import PaskitScene
from src.core.config import Config
from src.core.events import get_event_bus
from src.ai import AnthropicProvider, ManimPromptBuilder, CodeParser
from src.execution import ManimExecutor
from src.utils import get_icon_path
import asyncio


def set_title_bar_color(hwnd, color):
    """Set Windows title bar color using DWM API."""
    if sys.platform != 'win32':
        return
    try:
        DWMWA_CAPTION_COLOR = 35
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_CAPTION_COLOR,
            ctypes.byref(ctypes.c_int(color)),
            ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass


class ManimRenderPanel(QWidget):
    """Panel for rendering ManimGL scenes using QPainter with camera controls."""

    # Signals
    settings_clicked = pyqtSignal()

    # Dark background color matching right side of window
    BG_COLOR = "#2b2b2b"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = None
        self.renderer = None
        self.last_update_time = None

        # Camera control state
        self.camera_offset_x = 0.0  # Offset in ManimGL units
        self.camera_offset_y = 0.0
        self.camera_scale = 1.0  # Zoom level (1.0 = default)

        # 3D camera rotation
        self.camera_theta = 0.0  # Horizontal rotation (degrees)
        self.camera_phi = 0.0    # Vertical rotation (degrees)

        # Frame buffer for threaded rendering
        self.frame_buffer = None
        self.render_mutex = QMutex()

        # Mouse state
        self.is_panning = False
        self.is_rotating = False

        # Install event filter to intercept wheel events from children
        self.installEventFilter(self)
        self.pan_start_pos = None
        self.pan_start_offset = None
        self.rotate_start_pos = None
        self.rotate_start_angles = None

        # Enable mouse tracking for smooth panning
        self.setMouseTracking(True)

        # Create layout for timeline at bottom
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add spacer to push timeline to bottom
        layout.addStretch()

        # Askit branding label (above timeline, right-aligned, 3x larger, code font)
        brand_container = QWidget()
        brand_layout = QHBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 24, 8)
        brand_layout.addStretch()
        self.brand_label = QLabel("Askit.")
        self.brand_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 42px;
                font-weight: bold;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                background: transparent;
            }
        """)
        brand_layout.addWidget(self.brand_label)
        layout.addWidget(brand_container)

        # Create timeline widget
        self.timeline = AnimationTimeline(self)
        layout.addWidget(self.timeline)

        # Connect timeline signals
        self.timeline.play_requested.connect(self.on_play_requested)
        self.timeline.play_reverse_requested.connect(self.on_play_reverse_requested)
        self.timeline.pause_requested.connect(self.on_pause_requested)
        self.timeline.seek_requested.connect(self.on_seek_requested)

        # Create HUD overlay for controls (positioned on top of render area)
        self.hud_overlay = HUDControlOverlay(self)
        self.hud_overlay.control_changed.connect(self.on_control_changed)

        # Install event filter on child widgets to intercept wheel events
        self.timeline.installEventFilter(self)
        self.hud_overlay.installEventFilter(self)

        # Set up timer for continuous rendering (default 60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_update)
        self.timer.start(16)  # Default ~60 FPS, can be changed via set_framerate()

        # Button style for top-left controls
        btn_style = """
            QPushButton {
                background: rgba(60, 60, 60, 0.8);
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 80, 0.9);
            }
            QPushButton:checked {
                background: rgba(90, 130, 180, 0.9);
            }
        """

        # Settings button (top-left corner, first)
        self.settings_btn = QPushButton(self)
        self.settings_btn.setFixedSize(44, 44)
        self.settings_btn.setIconSize(QSize(28, 28))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setStyleSheet(btn_style)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.settings_btn.move(8, 8)

        # Load settings icon
        from PyQt5.QtGui import QIcon
        settings_icon_path = get_icon_path("settings")
        if os.path.exists(settings_icon_path):
            self.settings_btn.setIcon(QIcon(settings_icon_path))

        # Reset button (next to settings)
        self.reset_btn = QPushButton(self)
        self.reset_btn.setFixedSize(44, 44)
        self.reset_btn.setIconSize(QSize(28, 28))
        self.reset_btn.setToolTip("Reset view to origin")
        self.reset_btn.clicked.connect(self.reset_camera)
        self.reset_btn.setStyleSheet(btn_style)
        self.reset_btn.move(60, 8)

        # Load home icon
        home_icon_path = get_icon_path("home")
        if os.path.exists(home_icon_path):
            self.reset_btn.setIcon(QIcon(home_icon_path))

        # 2D/3D toggle button (next to reset)
        self.view_3d_btn = QPushButton(self)
        self.view_3d_btn.setFixedSize(44, 44)
        self.view_3d_btn.setIconSize(QSize(28, 28))
        self.view_3d_btn.setToolTip("Toggle 2D/3D view")
        self.view_3d_btn.setCheckable(True)
        self.view_3d_btn.setChecked(False)
        self.view_3d_btn.clicked.connect(self.toggle_3d_view)
        self.view_3d_btn.setStyleSheet(btn_style)
        self.view_3d_btn.move(112, 8)

        # Load cube icon for 3D mode (default shows cube = click to go 3D)
        cube_icon_path = get_icon_path("cube")
        if os.path.exists(cube_icon_path):
            self.view_3d_btn.setIcon(QIcon(cube_icon_path))

        # 3D view state
        self.is_3d_view = False
        self.target_phi = 0.0
        self.target_theta = 0.0
        self.animation_timer = None

        # Zoom animation state
        self.target_scale = 1.0
        self.zoom_animating = False

        # Axis labels (stay at screen edges, large italic)
        label_style = """
            QLabel {
                color: #aaa;
                font-size: 36px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
                background: transparent;
            }
        """
        self.x_label = QLabel("x", self)
        self.x_label.setStyleSheet(label_style)
        self.x_label.setFixedSize(40, 45)

        self.y_label = QLabel("y", self)
        self.y_label.setStyleSheet(label_style)
        self.y_label.setFixedSize(40, 45)

        # Z label (hidden by default, shown in 3D mode)
        self.z_label = QLabel("z", self)
        self.z_label.setStyleSheet(label_style)
        self.z_label.setFixedSize(40, 45)
        self.z_label.hide()

        # Initialize scene
        self.initialize_scene()

    def initialize_scene(self):
        """Initialize PaskitScene and QPainter renderer."""
        from loguru import logger
        from src.manim_bridge.qpainter_renderer import QPainterRenderer

        logger.info("[ManimRenderPanel] Initializing PaskitScene...")

        try:
            # Create PaskitScene (enable animations)
            self.scene = PaskitScene(qt_widget=self, skip_animations=False)

            # Create QPainter renderer
            self.renderer = QPainterRenderer(width=1920, height=1080)

            logger.info("[ManimRenderPanel] PaskitScene and QPainter renderer created successfully")
        except Exception as e:
            logger.exception(f"[ManimRenderPanel] Failed to initialize: {e}")

    def on_timer_update(self):
        """Timer callback for real-time animation updates."""
        import time

        # Calculate time delta
        current_time = time.time()
        if self.last_update_time is not None:
            dt = current_time - self.last_update_time
            # Skip frame if too much time passed (avoid large jumps)
            if dt > 0.1:
                dt = 0.016
        else:
            dt = 0.016  # ~60 FPS default

        self.last_update_time = current_time

        # Update scene animation timeline (only if scene exists)
        if self.scene:
            self.scene.update(dt)

            # Update timeline widget display
            self.timeline.set_current_time(self.scene.timeline.current_time)
            self.timeline.set_duration(self.scene.timeline.total_duration)

        # Render to buffer and trigger repaint
        if self.isVisible():
            self._render_to_buffer()
            self.update()

    def set_framerate(self, fps: int):
        """Set the rendering framerate.

        Args:
            fps: Target frames per second (0 = unlimited/1ms)
        """
        if fps <= 0:
            interval = 1  # 1ms for "unlimited"
        else:
            interval = max(1, int(1000 / fps))

        self.timer.setInterval(interval)
        from loguru import logger
        logger.info(f"[ManimRenderPanel] Framerate set to {fps} FPS (interval: {interval}ms)")

    def on_play_requested(self):
        """Handle play button click."""
        from loguru import logger
        logger.info("[ManimRenderPanel] Play requested")
        if self.scene:
            self.scene.timeline.play()

    def on_play_reverse_requested(self):
        """Handle reverse play button click."""
        from loguru import logger
        logger.info("[ManimRenderPanel] Reverse play requested")
        if self.scene:
            self.scene.timeline.play_reverse()

    def on_pause_requested(self):
        """Handle pause button click."""
        from loguru import logger
        logger.info("[ManimRenderPanel] Pause requested")
        if self.scene:
            self.scene.timeline.pause()

    def on_seek_requested(self, time: float, snap: bool = True):
        """Handle timeline seek."""
        from loguru import logger
        logger.info(f"[ManimRenderPanel] Seek requested to {time:.2f}s (snap={snap})")
        if self.scene:
            self.scene.seek_to_time(time, snap)

    def on_control_changed(self, name: str, value):
        """Handle HUD control value change."""
        from loguru import logger
        logger.debug(f"[ManimRenderPanel] Control changed: {name} = {value}")
        # Store in scene variables if scene exists
        if self.scene and hasattr(self.scene, 'snapshot_manager'):
            self.scene.snapshot_manager.set_variable(name, value)

    def resizeEvent(self, event):
        """Handle resize to adjust HUD overlay and renderer."""
        super().resizeEvent(event)
        # Resize HUD overlay to match panel (minus timeline height)
        timeline_height = self.timeline.height() if hasattr(self, 'timeline') else 40
        if hasattr(self, 'hud_overlay'):
            self.hud_overlay.setGeometry(0, 0, self.width(), self.height() - timeline_height)

        # Update renderer dimensions to match widget
        if self.renderer:
            self.renderer.width = self.width()
            self.renderer.height = self.height()
            self.renderer.scale_x = self.renderer.width / self.renderer.frame_width
            self.renderer.scale_y = self.renderer.height / self.renderer.frame_height
            self.renderer.uniform_scale = min(self.renderer.scale_x, self.renderer.scale_y)
            self.renderer.center_offset_x = (self.renderer.width - self.renderer.frame_width * self.renderer.uniform_scale) / 2
            self.renderer.center_offset_y = (self.renderer.height - self.renderer.frame_height * self.renderer.uniform_scale) / 2

        # Update axis label positions
        self._update_axis_labels()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning and rotating."""
        if event.button() == Qt.LeftButton:
            # Left click = pan
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.pan_start_offset = (self.camera_offset_x, self.camera_offset_y)
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.RightButton:
            # Right click = rotate (only in 3D mode)
            if self.is_3d_view:
                self.is_rotating = True
                self.rotate_start_pos = event.pos()
                self.rotate_start_angles = (self.camera_theta, self.camera_phi)
                self.setCursor(Qt.SizeAllCursor)
            event.accept()
        elif event.button() == Qt.MiddleButton:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning and rotating."""
        if self.is_panning and self.pan_start_pos is not None:
            delta = event.pos() - self.pan_start_pos

            # Scale factor considers both base frame width AND current zoom level
            base_frame_width = 14.222222222222221
            scale_factor = (base_frame_width * self.camera_scale) / self.width()

            # Natural panning: drag direction moves content in same direction
            dx = -delta.x() * scale_factor
            dy = delta.y() * scale_factor

            self.camera_offset_x = self.pan_start_offset[0] + dx
            self.camera_offset_y = self.pan_start_offset[1] + dy

            self.update_camera()
            event.accept()
        elif self.is_rotating and self.rotate_start_pos is not None:
            delta = event.pos() - self.rotate_start_pos
            sensitivity = 0.5

            self.camera_theta = self.rotate_start_angles[0] + delta.x() * sensitivity
            self.camera_phi = self.rotate_start_angles[1] + delta.y() * sensitivity

            # Clamp phi to avoid gimbal lock
            self.camera_phi = max(-89, min(89, self.camera_phi))

            self.update_camera()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to stop panning/rotating."""
        if event.button() == Qt.LeftButton and self.is_panning:
            self.is_panning = False
            self.pan_start_pos = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        elif event.button() == Qt.RightButton and self.is_rotating:
            self.is_rotating = False
            self.rotate_start_pos = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for smooth center-fixed zooming."""
        event.accept()
        self._handle_zoom(event.angleDelta().y())

    def _handle_zoom(self, delta: int):
        """Handle zoom with smooth animation, center-fixed."""
        if delta == 0:
            return

        # Calculate new target scale (scroll up = zoom in, scroll down = zoom out)
        zoom_factor = 0.9 if delta > 0 else 1.1
        self.target_scale = self.camera_scale * zoom_factor
        self.target_scale = max(0.1, min(10.0, self.target_scale))

        # Start smooth zoom animation if not already animating
        if not self.zoom_animating:
            self.zoom_animating = True
            self._animate_zoom()

    def eventFilter(self, obj, event):
        """Intercept wheel events from all child widgets."""
        from PyQt5.QtCore import QEvent
        if event.type() == QEvent.Wheel:
            self._handle_zoom(event.angleDelta().y())
            return True  # Event handled
        return super().eventFilter(obj, event)

    def update_camera(self):
        """Update renderer with current camera settings."""
        if self.renderer:
            # Update renderer's frame dimensions based on zoom
            base_width = 14.222222222222221
            base_height = 8.0

            self.renderer.frame_width = base_width * self.camera_scale
            self.renderer.frame_height = base_height * self.camera_scale

            # Update scale factors
            self.renderer.scale_x = self.renderer.width / self.renderer.frame_width
            self.renderer.scale_y = self.renderer.height / self.renderer.frame_height

            # CRITICAL: Update uniform_scale for proper rendering
            self.renderer.uniform_scale = min(self.renderer.scale_x, self.renderer.scale_y)

            # Update center offsets for proper centering
            self.renderer.center_offset_x = (self.renderer.width - self.renderer.frame_width * self.renderer.uniform_scale) / 2
            self.renderer.center_offset_y = (self.renderer.height - self.renderer.frame_height * self.renderer.uniform_scale) / 2

            # Store camera offset for rendering
            self.renderer.camera_offset_x = self.camera_offset_x
            self.renderer.camera_offset_y = self.camera_offset_y

            # Store rotation angles for 3D rendering
            self.renderer.camera_theta = self.camera_theta
            self.renderer.camera_phi = self.camera_phi

        # Update axis labels
        self._update_axis_labels()
        self.update()

    def reset_camera(self):
        """Reset camera to default position and zoom with animation, keeping current 2D/3D mode."""
        # Set targets for animation (keep current 2D/3D mode)
        self.target_offset_x = 0.0
        self.target_offset_y = 0.0
        self.target_scale = 1.0

        # Keep current view mode angles
        if self.is_3d_view:
            self.target_theta = 45.0
            self.target_phi = 30.0
        else:
            self.target_theta = 0.0
            self.target_phi = 0.0

        # Start reset animation
        self._animate_reset()

    def toggle_3d_view(self):
        """Toggle between 2D and 3D view with smooth animation."""
        import os
        from PyQt5.QtGui import QIcon

        self.is_3d_view = not self.is_3d_view

        if self.is_3d_view:
            self.target_theta = 45.0
            self.target_phi = 30.0
            # Switch to plane icon (click to go back to 2D)
            plane_path = get_icon_path("plane")
            if os.path.exists(plane_path):
                self.view_3d_btn.setIcon(QIcon(plane_path))
            # Add z-axis for 3D mode
            self._setup_3d_axes()
            # Show z label
            self.z_label.show()
        else:
            self.target_theta = 0.0
            self.target_phi = 0.0
            # Switch to cube icon (click to go to 3D)
            cube_path = get_icon_path("cube")
            if os.path.exists(cube_path):
                self.view_3d_btn.setIcon(QIcon(cube_path))
            # Remove z-axis for 2D mode
            self._setup_2d_axes()
            # Hide z label
            self.z_label.hide()

        # Start animation
        self._animate_view_transition()

    def _setup_3d_axes(self):
        """Setup 3D axes with 3D tick marks on all axes."""
        if not self.scene:
            return
        from manimlib import Line, VGroup

        # Remove old axes
        if hasattr(self.scene, 'axes') and self.scene.axes in self.scene.mobjects:
            self.scene.remove(self.scene.axes)
        if hasattr(self, 'axes_3d_group') and self.axes_3d_group in self.scene.mobjects:
            self.scene.remove(self.axes_3d_group)

        # Create 3D axes group with cross tick marks
        self.axes_3d_group = VGroup()

        # X-axis line
        x_line = Line(
            start=[-20, 0, 0],
            end=[20, 0, 0],
            stroke_color="#666666",
            stroke_width=2
        )
        self.axes_3d_group.add(x_line)

        # Y-axis line
        y_line = Line(
            start=[0, -20, 0],
            end=[0, 20, 0],
            stroke_color="#666666",
            stroke_width=2
        )
        self.axes_3d_group.add(y_line)

        # Z-axis line
        z_line = Line(
            start=[0, 0, -20],
            end=[0, 0, 20],
            stroke_color="#666666",
            stroke_width=2
        )
        self.axes_3d_group.add(z_line)

        # Add 3D cross tick marks on X-axis
        for x in range(-20, 21, 1):
            if x == 0:
                continue
            tick_y = Line(start=[x, -0.05, 0], end=[x, 0.05, 0],
                         stroke_color="#666666", stroke_width=1)
            tick_z = Line(start=[x, 0, -0.05], end=[x, 0, 0.05],
                         stroke_color="#666666", stroke_width=1)
            self.axes_3d_group.add(tick_y, tick_z)

        # Add 3D cross tick marks on Y-axis
        for y in range(-20, 21, 1):
            if y == 0:
                continue
            tick_x = Line(start=[-0.05, y, 0], end=[0.05, y, 0],
                         stroke_color="#666666", stroke_width=1)
            tick_z = Line(start=[0, y, -0.05], end=[0, y, 0.05],
                         stroke_color="#666666", stroke_width=1)
            self.axes_3d_group.add(tick_x, tick_z)

        # Add 3D cross tick marks on Z-axis
        for z in range(-20, 21, 1):
            if z == 0:
                continue
            tick_x = Line(start=[-0.05, 0, z], end=[0.05, 0, z],
                         stroke_color="#666666", stroke_width=1)
            tick_y = Line(start=[0, -0.05, z], end=[0, 0.05, z],
                         stroke_color="#666666", stroke_width=1)
            self.axes_3d_group.add(tick_x, tick_y)

        self.scene.add(self.axes_3d_group)
        # Store reference for compatibility
        self.scene.axes = self.axes_3d_group

    def _setup_2d_axes(self):
        """Setup 2D axes without z-axis."""
        if not self.scene:
            return

        # Remove 3D axes group if exists
        if hasattr(self, 'axes_3d_group') and self.axes_3d_group in self.scene.mobjects:
            self.scene.remove(self.axes_3d_group)

        # Remove old axes
        if hasattr(self.scene, 'axes') and self.scene.axes in self.scene.mobjects:
            self.scene.remove(self.scene.axes)

        # Create extended 2D axes
        from manimlib import Axes
        self.scene.axes = Axes(
            x_range=[-20, 20, 1],
            y_range=[-20, 20, 1],
            axis_config={"stroke_color": "#666666", "stroke_width": 2},
        )
        self.scene.add(self.scene.axes)

    def _animate_view_transition(self):
        """Animate smooth transition between 2D and 3D views."""
        # Animation parameters
        speed = 0.15  # Interpolation speed

        # Calculate difference
        d_theta = self.target_theta - self.camera_theta
        d_phi = self.target_phi - self.camera_phi

        # Check if animation is complete
        if abs(d_theta) < 0.5 and abs(d_phi) < 0.5:
            self.camera_theta = self.target_theta
            self.camera_phi = self.target_phi
            self.update_camera()
            return

        # Interpolate
        self.camera_theta += d_theta * speed
        self.camera_phi += d_phi * speed
        self.update_camera()

        # Schedule next frame
        QTimer.singleShot(16, self._animate_view_transition)

    def _animate_reset(self):
        """Animate smooth reset to origin."""
        speed = 0.15

        # Calculate differences
        d_x = self.target_offset_x - self.camera_offset_x
        d_y = self.target_offset_y - self.camera_offset_y
        d_scale = self.target_scale - self.camera_scale
        d_theta = self.target_theta - self.camera_theta
        d_phi = self.target_phi - self.camera_phi

        # Check if animation is complete
        done = (abs(d_x) < 0.01 and abs(d_y) < 0.01 and
                abs(d_scale) < 0.01 and abs(d_theta) < 0.5 and abs(d_phi) < 0.5)

        if done:
            self.camera_offset_x = self.target_offset_x
            self.camera_offset_y = self.target_offset_y
            self.camera_scale = self.target_scale
            self.camera_theta = self.target_theta
            self.camera_phi = self.target_phi
            self.update_camera()
            return

        # Interpolate all values
        self.camera_offset_x += d_x * speed
        self.camera_offset_y += d_y * speed
        self.camera_scale += d_scale * speed
        self.camera_theta += d_theta * speed
        self.camera_phi += d_phi * speed
        self.update_camera()

        QTimer.singleShot(16, self._animate_reset)

    def _update_axis_labels(self):
        """Update axis label positions to stay at screen edges near axes."""
        if not hasattr(self, 'x_label') or not self.renderer:
            return

        # Get the screen position of the origin
        origin_sx = self._manim_x_to_screen(0)
        origin_sy = self._manim_y_to_screen(0)

        # X label: position at right edge of screen, vertically aligned with x-axis
        x_lx = self.width() - 45
        x_ly = int(origin_sy) - 20
        x_ly = max(50, min(self.height() - 100, x_ly))
        self.x_label.move(x_lx, x_ly)

        # Y label: position at top edge of screen, horizontally aligned with y-axis
        y_lx = int(origin_sx) + 10
        y_ly = 50
        y_lx = max(50, min(self.width() - 60, y_lx))
        self.y_label.move(y_lx, y_ly)

        # Z label: only visible in 3D mode, moves with camera
        if self.is_3d_view and hasattr(self, 'z_label'):
            # Calculate z-axis screen position based on 3D rotation
            import numpy as np
            theta = np.radians(self.camera_theta)
            phi = np.radians(self.camera_phi)

            # Z-axis end point in 3D
            z_end = np.array([0, 0, 5.0])

            # Apply rotation
            z_rot = z_end[2] * np.cos(phi)
            y_from_z = z_end[2] * np.sin(phi)

            # Convert to screen
            z_sx = self._manim_x_to_screen(0)
            z_sy = self._manim_y_to_screen(y_from_z)

            z_lx = int(z_sx) - 20
            z_ly = int(z_sy) - 20
            z_ly = max(50, min(self.height() - 100, z_ly))
            z_lx = max(50, min(self.width() - 60, z_lx))
            self.z_label.move(z_lx, z_ly)

    def _manim_x_to_screen(self, x: float) -> float:
        """Convert manim x coordinate to screen x."""
        x_offset = x - self.camera_offset_x
        return (x_offset + self.renderer.frame_width / 2) * self.renderer.uniform_scale + self.renderer.center_offset_x

    def _manim_y_to_screen(self, y: float) -> float:
        """Convert manim y coordinate to screen y."""
        y_offset = y - self.camera_offset_y
        return (self.renderer.frame_height / 2 - y_offset) * self.renderer.uniform_scale + self.renderer.center_offset_y

    def _animate_zoom(self):
        """Animate smooth zoom transition with easing."""
        # Smoother interpolation with easing
        speed = 0.25

        d_scale = self.target_scale - self.camera_scale

        # Check if animation is complete
        if abs(d_scale) < 0.005:
            self.camera_scale = self.target_scale
            self.zoom_animating = False
            self.update_camera()
            return

        # Apply easing for smoother animation
        self.camera_scale += d_scale * speed
        self.update_camera()

        # Continue animation at ~60fps
        QTimer.singleShot(16, self._animate_zoom)

    def _render_to_buffer(self):
        """Render scene to buffer image."""
        if not self.scene or not self.renderer:
            return
        from PyQt5.QtGui import QColor
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return
        img = QImage(w, h, QImage.Format_RGB32)
        img.fill(QColor(self.BG_COLOR))
        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing, True)
        try:
            self.renderer.bg_color = QColor(self.BG_COLOR)
            self.renderer.render(painter, self.scene.mobjects)
        except:
            pass
        painter.end()
        with QMutexLocker(self.render_mutex):
            self.frame_buffer = img

    def paintEvent(self, event):
        """Paint cached frame buffer."""
        from PyQt5.QtGui import QColor
        painter = QPainter(self)
        with QMutexLocker(self.render_mutex):
            if self.frame_buffer:
                painter.drawImage(0, 0, self.frame_buffer)
            else:
                painter.fillRect(self.rect(), QColor(self.BG_COLOR))
        painter.end()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: Config, event_bus):
        from loguru import logger
        logger.info("[MainWindow] __init__ started")

        super().__init__()
        self.config = config
        self.event_bus = event_bus

        logger.info("[MainWindow] Window configured")

        # Initialize AI components
        logger.info("[MainWindow] Initializing AI provider...")
        self.initialize_ai_provider()
        logger.info("[MainWindow] AI provider initialized")

        logger.info("[MainWindow] Creating prompt builder...")
        self.prompt_builder = ManimPromptBuilder()
        logger.info("[MainWindow] Creating code parser...")
        self.code_parser = CodeParser()
        self.executor = None  # Will be set after scene is created
        logger.info("[MainWindow] AI components created")

        logger.info("[MainWindow] Setting up UI...")
        self.setup_ui()
        logger.info("[MainWindow] UI setup completed")

        logger.info("[MainWindow] Setting up connections...")
        self.setup_connections()
        logger.info("[MainWindow] __init__ completed")

    def initialize_ai_provider(self):
        """Initialize AI provider based on current configuration."""
        from src.ai import OpenAIProvider

        provider_name = self.config.current_provider
        provider_config = getattr(self.config, provider_name, None)

        if not provider_config or not provider_config.api_key:
            # No API key configured, create a dummy provider
            self.ai_provider = None
            return

        # Create provider based on type
        if provider_name in ['openai', 'ollama']:
            self.ai_provider = OpenAIProvider(
                api_key=provider_config.api_key,
                base_url=provider_config.base_url,
                model=provider_config.default_model or "gpt-4"
            )
        elif provider_name == 'anthropic':
            self.ai_provider = AnthropicProvider(provider_config.api_key)
        else:
            self.ai_provider = None

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Askit.")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(800, 600)

        # Set dark title bar color using Windows DWM API
        # Color format: 0x00BBGGRR
        dark_color = 0x002b2b2b  # #2b2b2b in BGR
        set_title_bar_color(int(self.winId()), dark_color)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2b2b2b;
            }
        """)

        # Left panel: Chat (light gray)
        self.chat_panel = ChatPanel()
        self.chat_panel.settings_clicked.connect(self.open_settings)
        self.splitter.addWidget(self.chat_panel)

        # Right panel: ManimGL rendering (dark)
        self.render_panel = ManimRenderPanel()
        self.splitter.addWidget(self.render_panel)

        # Apply framerate from config
        self.render_panel.set_framerate(self.config.rendering.target_fps)

        # Set initial sizes
        self.splitter.setSizes([350, 1250])

        layout.addWidget(self.splitter)

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Reload config after settings are saved
            self.config = Config.load()
            # Reinitialize AI provider with new config
            self.initialize_ai_provider()
            # Apply new framerate
            self.render_panel.set_framerate(self.config.rendering.target_fps)

    def setup_connections(self):
        """Set up signal connections."""
        self.chat_panel.message_sent.connect(self.on_message_sent)
        self.chat_panel.message_sent_with_files.connect(self.on_message_sent_with_files)
        self.render_panel.settings_clicked.connect(self.open_settings)

    def on_message_sent(self, message: str):
        """Handle user message."""
        from loguru import logger
        logger.info(f"[on_message_sent] Processing: {message}")

        # Initialize executor if needed (use HUD overlay for controls)
        if self.executor is None and self.render_panel.scene:
            self.executor = ManimExecutor(self.render_panel.scene, self.render_panel.hud_overlay)

        # Process message asynchronously
        asyncio.create_task(self.process_message(message))

    def on_message_sent_with_files(self, message: str, file_paths: list):
        """Handle user message with attached files."""
        from loguru import logger
        import os

        logger.info(f"[on_message_sent_with_files] Processing message with {len(file_paths)} files")

        # Supported file formats
        SUPPORTED_TEXT_FORMATS = {'.txt', '.py', '.md', '.json', '.csv', '.xml', '.html', '.css', '.js'}
        SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

        # Initialize executor if needed
        if self.executor is None and self.render_panel.scene:
            self.executor = ManimExecutor(self.render_panel.scene, self.render_panel.hud_overlay)

        # Process files and build enhanced message
        enhanced_message = message if message else "请分析这些文件："
        file_contents = []

        for file_path in file_paths:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)

            # Validate file format
            if file_ext not in SUPPORTED_TEXT_FORMATS and file_ext not in SUPPORTED_IMAGE_FORMATS:
                logger.warning(f"[on_message_sent_with_files] Unsupported file format: {file_ext}")
                self.chat_panel.add_message("AI", f"⚠ 不支持的文件格式: {file_name} ({file_ext})\n支持的格式: {', '.join(SUPPORTED_TEXT_FORMATS | SUPPORTED_IMAGE_FORMATS)}")
                continue

            # Read text files
            if file_ext in SUPPORTED_TEXT_FORMATS:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_contents.append(f"\n\n--- 文件: {file_name} ---\n{content}\n--- 文件结束 ---")
                    logger.info(f"[on_message_sent_with_files] Read text file: {file_name} ({len(content)} chars)")
                except Exception as e:
                    logger.error(f"[on_message_sent_with_files] Failed to read {file_name}: {e}")
                    self.chat_panel.add_message("AI", f"✗ 无法读取文件: {file_name}\n错误: {str(e)}")

            # Handle image files (for future implementation)
            elif file_ext in SUPPORTED_IMAGE_FORMATS:
                file_contents.append(f"\n\n[图片文件: {file_name}]")
                logger.info(f"[on_message_sent_with_files] Image file noted: {file_name}")

        # Combine message with file contents
        if file_contents:
            enhanced_message += "\n" + "".join(file_contents)

        # Process enhanced message asynchronously
        asyncio.create_task(self.process_message(enhanced_message))

    async def process_message(self, message: str):
        """Process user message with AI."""
        from loguru import logger
        import re
        logger.info(f"[process_message] Started processing: {message}")

        # Start loading animation
        self.chat_panel.start_loading()

        try:
            # Check if AI provider is configured
            if self.ai_provider is None:
                logger.warning("[process_message] No AI provider configured")
                self.chat_panel.stop_loading()
                self.chat_panel.add_message("AI", "Error: No AI provider configured. Please click the settings button to configure your API key.")
                return

            # Get scene context from snapshot manager
            scene_context = None
            if self.render_panel.scene and hasattr(self.render_panel.scene, 'snapshot_manager'):
                scene_context = self.render_panel.scene.snapshot_manager.get_current_context()
                logger.info(f"[process_message] Scene context: {len(scene_context)} chars")

            # Build prompt with scene context
            logger.info("[process_message] Building prompt...")
            prompt = self.prompt_builder.build_prompt(message, scene_context)

            # Stream callback to update progress bar
            def on_stream(delta: str, total_chars: int):
                self.chat_panel.loading_widget.update_progress(total_chars)

            # Get AI response with streaming
            logger.info("[process_message] Requesting AI response...")
            response = await self.ai_provider.generate(prompt, stream_callback=on_stream)
            logger.info(f"[process_message] Received response: {len(response)} chars")

            # Stop loading animation
            self.chat_panel.stop_loading()

            # Extract text before code block
            text_before = re.split(r'```python', response, maxsplit=1)[0].strip()
            if text_before:
                self.chat_panel.add_message("AI", text_before)

            # Parse code
            logger.info("[process_message] Parsing code...")
            code = self.code_parser.extract_first_code_block(response)

            # Extract text after code block
            code_match = re.search(r'```python.*?```', response, re.DOTALL)
            if code_match:
                text_after = response[code_match.end():].strip()
                text_after = re.sub(r'^```\s*', '', text_after)  # Remove trailing ```
                if text_after:
                    self.chat_panel.add_message("AI", text_after)

            # Execute code
            if not code:
                logger.warning("[process_message] No code block found in response")
                return

            logger.info(f"[process_message] Extracted code: {len(code)} chars")

            # Display code (hidden by default)
            self.chat_panel.add_code_block(code, hidden=True)

            logger.info(f"[process_message] Executor exists: {self.executor is not None}")
            if self.executor:
                logger.info("[process_message] Executing code...")
                result = self.executor.execute(code)
                logger.info(f"[process_message] Execution result: {result}")

                if result['success']:
                    logger.info("[process_message] Code executed successfully")
                    self.render_panel.update()
                else:
                    logger.error(f"[process_message] Execution failed: {result['error']}")
                    self.chat_panel.add_message("AI", f"✗ Error: {result['error']}")
            else:
                logger.warning("[process_message] Executor is None, cannot execute code")

        except Exception as e:
            self.chat_panel.stop_loading()
            logger.exception(f"[process_message] Exception: {e}")
            self.chat_panel.add_message("AI", f"Error: {str(e)}")
