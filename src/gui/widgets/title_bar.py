"""Custom title bar widget with Windows-style buttons."""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QMouseEvent


class TitleBar(QWidget):
    """Custom title bar with split colors and Windows-style buttons."""

    settings_clicked = pyqtSignal()
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    # Colors
    LEFT_BG = "#f0f0f0"   # Light gray (same as left panel)
    RIGHT_BG = "#2b2b2b"  # Dark gray (same as viewer)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self._drag_pos = None
        self._is_maximized = False
        self.setup_ui()

    def setup_ui(self):
        """Setup the title bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left section (light gray)
        self.left_section = QWidget()
        self.left_section.setStyleSheet(f"background-color: {self.LEFT_BG};")
        left_layout = QHBoxLayout(self.left_section)
        left_layout.setContentsMargins(12, 0, 12, 0)
        left_layout.setSpacing(8)

        # App icon/title
        self.title_label = QLabel("PAskit")
        self.title_label.setFont(QFont("Segoe UI", 9))
        self.title_label.setStyleSheet("color: #333; background: transparent;")
        left_layout.addWidget(self.title_label)

        left_layout.addStretch()
        layout.addWidget(self.left_section)

        # Right section (dark gray)
        self.right_section = QWidget()
        self.right_section.setStyleSheet(f"background-color: {self.RIGHT_BG};")
        right_layout = QHBoxLayout(self.right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        right_layout.addStretch()

        # Settings button (before window controls)
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(46, 32)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self._style_button(self.settings_btn, light=False)
        right_layout.addWidget(self.settings_btn)

        # Window controls
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(40, 28)
        self.min_btn.clicked.connect(self.minimize_clicked.emit)
        self._style_button(self.min_btn, light=False)

        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(40, 28)
        self.max_btn.clicked.connect(self.maximize_clicked.emit)
        self._style_button(self.max_btn, light=False)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 28)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        self._style_button(self.close_btn, light=False, is_close=True)

        right_layout.addWidget(self.min_btn)
        right_layout.addWidget(self.max_btn)
        right_layout.addWidget(self.close_btn)

        layout.addWidget(self.right_section)

    def _style_button(self, btn, light=True, is_close=False):
        """Apply button styling."""
        if light:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    color: #555;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
            """)
        else:
            hover_color = "#e81123" if is_close else "#3d3d3d"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: #aaa;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: {"#f1707a" if is_close else "#4d4d4d"};
                }}
            """)

    def set_split_ratio(self, left_ratio: float):
        """Set the ratio of left section width."""
        self.left_section.setFixedWidth(int(self.width() * left_ratio))

    def resizeEvent(self, event):
        """Handle resize to maintain split ratio."""
        super().resizeEvent(event)
        # Will be set by parent based on splitter position

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click to maximize/restore."""
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()

    def update_maximize_button(self, is_maximized: bool):
        """Update maximize button icon."""
        self._is_maximized = is_maximized
        self.max_btn.setText("❐" if is_maximized else "□")
