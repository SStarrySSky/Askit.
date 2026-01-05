"""
Activation dialog for PAskit license management.

Provides a JetBrains-style interface for entering activation codes.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon
from loguru import logger

from src.licensing import LicenseManager


class ActivationDialog(QDialog):
    """JetBrains-style activation dialog."""

    activation_successful = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize activation dialog."""
        super().__init__(parent)
        self.license_manager = LicenseManager()
        self.setup_ui()
        self.setWindowTitle("PAskit - Activation")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(48, 48, 48, 48)

        # Title
        title = QLabel("Activate Askit.")
        title_font = QFont("Segoe UI", 28, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #808080;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Enter your activation code to get started")
        subtitle_font = QFont("Segoe UI", 14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        # Activation code input
        code_label = QLabel("Activation Code:")
        code_label_font = QFont("Segoe UI", 13, QFont.Bold)
        code_label.setFont(code_label_font)
        code_label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(code_label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter your activation code (format: XXXX-XXXX-XXXX-...)")
        self.code_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """
        )
        self.code_input.setMinimumHeight(56)
        layout.addWidget(self.code_input)

        layout.addSpacing(24)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        # Activate button
        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setMinimumHeight(52)
        self.activate_btn.setMinimumWidth(160)
        self.activate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1084d7;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """
        )
        self.activate_btn.clicked.connect(self.on_activate_clicked)
        button_layout.addWidget(self.activate_btn)

        # Exit button
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setMinimumHeight(52)
        self.exit_btn.setMinimumWidth(160)
        self.exit_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #505050;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #454545;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """
        )
        self.exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.exit_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Set dialog size - much larger
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        # Dark theme
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1e1e1e;
            }
        """
        )

    def on_activate_clicked(self):
        """Handle activation button click."""
        code = self.code_input.text().strip()

        if not code:
            QMessageBox.warning(self, "Error", "Please enter an activation code")
            return

        # Validate and save license
        success, message = self.license_manager.save_license(code)

        if success:
            QMessageBox.information(self, "Success", message)
            self.activation_successful.emit()
            self.accept()
        else:
            QMessageBox.critical(self, "Activation Failed", message)
            logger.error(f"[ActivationDialog] Activation failed: {message}")

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_activate_clicked()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
