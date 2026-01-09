"""Chat panel for AI interaction with modern UI."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QFileDialog,
    QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPainter, QColor, QPen
import os
from src.utils import get_icon_path


class LoadingWidget(QWidget):
    """Progress bar for AI streaming response."""

    BG_COLOR = "#2b2b2b"  # Dark gray matching right panel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(f"background-color: {self.BG_COLOR};")
        self.progress = 0  # 0-100
        self.chars_received = 0
        self.is_streaming = False
        self.hide()

    def start(self):
        """Start showing progress bar."""
        self.show()
        self.progress = 0
        self.chars_received = 0
        self.is_streaming = True
        self.update()

    def stop(self):
        """Stop and hide progress bar."""
        self.is_streaming = False
        self.hide()

    def update_progress(self, chars: int):
        """Update progress based on characters received."""
        self.chars_received = chars
        # Estimate progress (assume ~2000 chars typical response)
        self.progress = min(95, int(chars / 20))
        self.update()

    def paintEvent(self, event):
        """Paint the progress bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background first (gray matching left panel)
        painter.fillRect(self.rect(), QColor(54, 54, 54))  # #363636

        # Progress bar dimensions
        margin = 40
        bar_height = 6
        bar_y = (self.height() - bar_height) // 2

        # Background track (darker gray)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(50, 50, 50))
        painter.drawRoundedRect(margin, bar_y, self.width() - 2 * margin, bar_height, 3, 3)

        # Progress fill (blue)
        if self.progress > 0:
            fill_width = int((self.width() - 2 * margin) * self.progress / 100)
            painter.setBrush(QColor(100, 150, 220))
            painter.drawRoundedRect(margin, bar_y, fill_width, bar_height, 3, 3)

        # Text showing chars received
        painter.setPen(QColor(150, 150, 150))
        painter.setFont(QFont("Consolas", 9))
        text = f"{self.chars_received} chars"
        painter.drawText(self.width() - margin + 5, bar_y + bar_height + 3, text)

        painter.end()


class ToolbarButton(QPushButton):
    """Toolbar button with SVG icon and toggle support."""

    PURPLE = "#8b5cf6"  # Purple for active state

    def __init__(self, icon_name: str, tooltip: str, toggleable: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setToolTip(tooltip)
        self.setIconSize(QSize(28, 28))
        self._toggleable = toggleable
        self._active = False

        # Try to load SVG icon
        icon_path = get_icon_path(icon_name)
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))

        self._update_style()

        if toggleable:
            self.clicked.connect(self._toggle)

    def _toggle(self):
        self._active = not self._active
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.PURPLE};
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: #9d6ff7;
                }}
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)

    def is_active(self) -> bool:
        return self._active

    def set_active(self, active: bool):
        self._active = active
        self._update_style()


class FileChip(QWidget):
    """Chip widget for displaying selected file with remove button."""

    removed = pyqtSignal(str)  # Emits file path when removed

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(4)

        # File icon based on extension
        ext = os.path.splitext(self.file_path)[1].lower()
        icon_map = {
            '.png': '🖼', '.jpg': '🖼', '.jpeg': '🖼', '.gif': '🖼',
            '.pdf': '📄', '.txt': '📝', '.py': '🐍', '.json': '📋'
        }
        icon = icon_map.get(ext, '📎')

        # File name label
        file_name = os.path.basename(self.file_path)
        if len(file_name) > 20:
            file_name = file_name[:17] + '...'

        self.label = QLabel(f"{icon} {file_name}")
        self.label.setFont(QFont("Segoe UI", 9))
        self.label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self.label)

        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(18, 18)
        self.remove_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.remove_btn.clicked.connect(self._on_remove)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888;
                border: none;
                border-radius: 9px;
            }
            QPushButton:hover {
                background-color: #555;
                color: white;
            }
        """)
        layout.addWidget(self.remove_btn)

        # Chip style - use direct property setting for custom widgets
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(74, 74, 74))
        self.setPalette(palette)
        self.setFixedHeight(28)

    def _on_remove(self):
        self.removed.emit(self.file_path)


class ChatPanel(QWidget):
    """Chat panel with modern WeChat-style input."""

    message_sent = pyqtSignal(str)
    message_sent_with_files = pyqtSignal(str, list)  # message, file_paths
    settings_clicked = pyqtSignal()

    # Dark gray colors (slightly lighter than viewer #2b2b2b)
    BG_COLOR = "#363636"
    INPUT_BG = "#3a3a3a"
    CHAT_BG = "#3a3a3a"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files = []  # Track selected files
        self.file_chips = {}  # Map file_path -> FileChip widget
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setStyleSheet(f"background-color: {self.BG_COLOR};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title area (minimal, matches background)
        title_widget = QWidget()
        title_widget.setFixedHeight(12)
        title_widget.setStyleSheet(f"background-color: {self.BG_COLOR};")
        layout.addWidget(title_widget)

        # Chat display area (no scrollbars, soft wrap)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))
        self.chat_display.setLineWrapMode(QTextEdit.WidgetWidth)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.CHAT_BG};
                border: none;
                padding: 12px;
                color: white;
            }}
        """)
        layout.addWidget(self.chat_display, 1)

        # Loading animation widget
        self.loading_widget = LoadingWidget()
        layout.addWidget(self.loading_widget)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #4a4a4a; max-height: 1px;")
        layout.addWidget(divider)

        # Toolbar with icons
        toolbar = QWidget()
        toolbar.setFixedHeight(52)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(8)

        self.upload_btn = ToolbarButton("upload", "Upload file")
        self.upload_btn.clicked.connect(self.select_file)
        self.search_btn = ToolbarButton("search", "Web search", toggleable=True)
        self.annotation_btn = ToolbarButton("annotation", "Annotation")

        toolbar_layout.addWidget(self.upload_btn)
        toolbar_layout.addWidget(self.search_btn)
        toolbar_layout.addWidget(self.annotation_btn)
        toolbar_layout.addStretch()

        layout.addWidget(toolbar)

        # Input area (large text box like WeChat)
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setFont(QFont("Segoe UI", 10))
        self.input_field.setMinimumHeight(80)
        self.input_field.setMaximumHeight(150)
        self.input_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.INPUT_BG};
                border: none;
                padding: 12px;
                color: #e0e0e0;
            }}
        """)
        layout.addWidget(self.input_field)

        # Send button row (matches background)
        send_row = QWidget()
        send_row.setFixedHeight(50)
        send_row.setStyleSheet(f"background-color: {self.BG_COLOR};")
        send_layout = QHBoxLayout(send_row)
        send_layout.setContentsMargins(8, 0, 12, 4)

        # File chips container (shows selected files)
        self.file_chips_container = QWidget()
        self.file_chips_layout = QHBoxLayout(self.file_chips_container)
        self.file_chips_layout.setContentsMargins(0, 0, 8, 0)
        self.file_chips_layout.setSpacing(6)
        send_layout.addWidget(self.file_chips_container)

        send_layout.addStretch()

        # Arrow send button with SVG icon
        self.send_button = QPushButton()
        self.send_button.setFixedSize(44, 44)
        self.send_button.setIconSize(QSize(24, 24))
        self.send_button.clicked.connect(self.send_message)

        # Load send icon
        send_icon_path = get_icon_path("send")
        if os.path.exists(send_icon_path):
            self.send_button.setIcon(QIcon(send_icon_path))

        self.send_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid transparent;
                border-radius: 8px;
            }
            QPushButton:hover {
                border: 2px solid #666;
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                border: 2px solid #888;
                background-color: #555;
            }
        """)
        send_layout.addWidget(self.send_button)

        layout.addWidget(send_row)

    def send_message(self):
        """Send the current message."""
        message = self.input_field.toPlainText().strip()
        if message or self.selected_files:
            # Show message with file info
            display_msg = message
            if self.selected_files:
                file_names = [os.path.basename(f) for f in self.selected_files]
                display_msg = f"{message}\n[附件: {', '.join(file_names)}]" if message else f"[附件: {', '.join(file_names)}]"

            self.add_message("User", display_msg)

            # Emit with files if any
            if self.selected_files:
                self.message_sent_with_files.emit(message, self.selected_files.copy())
            else:
                self.message_sent.emit(message)

            self.input_field.clear()
            self.clear_selected_files()

    def start_loading(self):
        """Start the loading animation."""
        self.loading_widget.start()

    def stop_loading(self):
        """Stop the loading animation."""
        self.loading_widget.stop()

    def add_message(self, sender: str, message: str):
        """Add a message to the chat display."""
        self.chat_display.append(
            f"<p><b style='color:white'>{sender}:</b> <span style='color:white'>{message}</span></p>"
        )
        self.chat_display.moveCursor(QTextCursor.End)

    def add_code_block(self, code: str, hidden: bool = True):
        """Add a collapsible code block to the chat display."""
        if hidden:
            self.chat_display.append(
                f"<p style='color:#888; font-size:11px;'>"
                f"[Code executed - {len(code.splitlines())} lines]</p>"
            )
        else:
            self.chat_display.append(
                f"<pre style='background:#2a2a2a; padding:8px; color:white; "
                f"border-radius:4px; font-family:Consolas;'>{code}</pre>"
            )
        self.chat_display.moveCursor(QTextCursor.End)

    def select_file(self):
        """Open file dialog to select files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "所有文件 (*);;图片 (*.png *.jpg *.jpeg *.gif);;文档 (*.pdf *.txt)"
        )
        for path in file_paths:
            self.add_file(path)

    def add_file(self, file_path: str):
        """Add a file to the selection."""
        if file_path in self.selected_files:
            return  # Already added

        self.selected_files.append(file_path)

        # Create chip widget
        chip = FileChip(file_path)
        chip.removed.connect(self.remove_file)
        self.file_chips[file_path] = chip
        self.file_chips_layout.addWidget(chip)

    def remove_file(self, file_path: str):
        """Remove a file from the selection."""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)

        if file_path in self.file_chips:
            chip = self.file_chips.pop(file_path)
            self.file_chips_layout.removeWidget(chip)
            chip.deleteLater()

    def clear_selected_files(self):
        """Clear all selected files."""
        for path in list(self.selected_files):
            self.remove_file(path)

    def is_web_search_enabled(self) -> bool:
        """Check if web search is enabled."""
        return self.search_btn.is_active()
