#!/usr/bin/env python3
"""
PAskit Graphical Installer

A professional Windows installer with GUI using PyQt5.
"""

import sys
import os
import shutil
import winreg
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QProgressBar, QFileDialog,
    QMessageBox, QStackedWidget, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import QSize


class InstallThread(QThread):
    """Thread for installation process."""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, source_dir, install_dir, create_shortcuts):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.install_dir = Path(install_dir)
        self.create_shortcuts = create_shortcuts

    def run(self):
        """Run installation."""
        try:
            # Create installation directory
            self.status.emit("Creating installation directory...")
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.progress.emit(10)

            # Copy files
            files = [
                "PAskit.exe",
            ]

            total_files = len(files)
            for i, file in enumerate(files):
                src = self.source_dir / file
                if src.exists():
                    self.status.emit(f"Copying {file}...")
                    shutil.copy(src, self.install_dir / file)
                    progress = 10 + int((i + 1) / total_files * 60)
                    self.progress.emit(progress)

            # Create shortcuts
            if self.create_shortcuts:
                self.status.emit("Creating shortcuts...")
                self._create_shortcuts()
                self.progress.emit(85)

            # Create uninstaller
            self.status.emit("Creating uninstaller...")
            self._create_uninstaller()
            self.progress.emit(95)

            # Register application
            self.status.emit("Registering application...")
            self._register_application()
            self.progress.emit(97)

            self.status.emit("Installation completed!")
            self.progress.emit(100)
            self.finished.emit(True)

        except Exception as e:
            self.status.emit(f"Error: {str(e)}")
            self.finished.emit(False)

    def _create_shortcuts(self):
        """Create Start Menu and Desktop shortcuts."""
        try:
            import subprocess

            # Create Start Menu shortcut
            ps_cmd = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{os.path.expandvars('%APPDATA%')}\\Microsoft\\Windows\\Start Menu\\Programs\\PAskit.lnk')
            $Shortcut.TargetPath = '{self.install_dir}\\PAskit.exe'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-Command", ps_cmd], check=False)

            # Create Desktop shortcut
            ps_cmd = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{os.path.expandvars('%USERPROFILE%')}\\Desktop\\PAskit.lnk')
            $Shortcut.TargetPath = '{self.install_dir}\\PAskit.exe'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-Command", ps_cmd], check=False)
        except Exception as e:
            print(f"Warning: Could not create shortcuts: {e}")

    def _create_uninstaller(self):
        """Create uninstaller script."""
        uninstall_script = self.install_dir / "uninstall.bat"
        with open(uninstall_script, "w", encoding="utf-8") as f:
            f.write(f"""@echo off
REM PAskit Uninstaller
echo Uninstalling PAskit...
rmdir /s /q "{self.install_dir}"
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PAskit.lnk" 2>nul
del "%USERPROFILE%\\Desktop\\PAskit.lnk" 2>nul
reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PAskit" /f 2>nul
echo Uninstallation completed.
pause
""")

    def _register_application(self):
        """Register application in Windows Add/Remove Programs."""
        try:
            # Create registry key for uninstall information
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PAskit"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)

            # Set registry values
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "PAskit")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "PAskit Team")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(self.install_dir))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(self.install_dir / "uninstall.bat"))
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(self.install_dir / "PAskit.exe"))
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)

            winreg.CloseKey(key)
        except Exception as e:
            print(f"Warning: Could not register application: {e}")


class PaskitInstaller(QMainWindow):
    """Main installer window."""

    def __init__(self):
        super().__init__()
        # Get correct path for PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = Path(sys._MEIPASS)
            self.source_dir = base_path / "release" / "PAskit-Installer"
        else:
            # Running in normal Python
            self.source_dir = Path(__file__).parent.parent / "release" / "PAskit-Installer"

        self.install_dir = Path(os.path.expandvars("%ProgramFiles%")) / "PAskit"
        self.install_thread = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("PAskit Installer")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1084d7;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
            QProgressBar {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)

        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create pages
        self.welcome_page = self.create_welcome_page()
        self.install_page = self.create_install_page()
        self.progress_page = self.create_progress_page()
        self.finish_page = self.create_finish_page()

        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.install_page)
        self.stacked_widget.addWidget(self.progress_page)
        self.stacked_widget.addWidget(self.finish_page)

        self.stacked_widget.setCurrentWidget(self.welcome_page)

    def create_welcome_page(self):
        """Create welcome page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Welcome to PAskit Installer")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "PAskit - AI-powered interactive teaching software\n\n"
            "This wizard will guide you through the installation process.\n\n"
            "Click 'Next' to continue."
        )
        desc_font = QFont("Segoe UI", 11)
        desc.setFont(desc_font)
        desc.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(desc)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        next_btn = QPushButton("Next >")
        next_btn.setMinimumWidth(100)
        next_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.install_page))
        button_layout.addWidget(next_btn)

        exit_btn = QPushButton("Cancel")
        exit_btn.setMinimumWidth(100)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #505050;
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        exit_btn.clicked.connect(self.close)
        button_layout.addWidget(exit_btn)

        layout.addLayout(button_layout)
        return page

    def create_install_page(self):
        """Create installation options page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Installation Options")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Installation directory
        dir_label = QLabel("Installation Directory:")
        dir_label_font = QFont("Segoe UI", 11, QFont.Bold)
        dir_label.setFont(dir_label_font)
        layout.addWidget(dir_label)

        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setText(str(self.install_dir))
        self.dir_input.setMinimumHeight(36)
        dir_layout.addWidget(self.dir_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.setMaximumWidth(100)
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)

        layout.addLayout(dir_layout)

        # Checkboxes
        layout.addSpacing(16)

        self.shortcuts_check = QCheckBox("Create Start Menu shortcut")
        self.shortcuts_check.setChecked(True)
        self.shortcuts_check.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.shortcuts_check)

        self.desktop_check = QCheckBox("Create Desktop shortcut")
        self.desktop_check.setChecked(True)
        self.desktop_check.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.desktop_check)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        back_btn = QPushButton("< Back")
        back_btn.setMinimumWidth(100)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.welcome_page))
        button_layout.addWidget(back_btn)

        install_btn = QPushButton("Install")
        install_btn.setMinimumWidth(100)
        install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(install_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #505050;
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        return page

    def create_progress_page(self):
        """Create progress page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Installing PAskit...")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Status label
        self.status_label = QLabel("Preparing installation...")
        self.status_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(24)
        layout.addWidget(self.progress_bar)

        layout.addStretch()
        return page

    def create_finish_page(self):
        """Create finish page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        self.finish_title = QLabel("Installation Completed!")
        title_font = QFont("Segoe UI", 20, QFont.Bold)
        self.finish_title.setFont(title_font)
        layout.addWidget(self.finish_title)

        # Message
        self.finish_message = QLabel(
            "PAskit has been successfully installed.\n\n"
            "You can now:\n"
            "- Run PAskit from the Start Menu\n"
            "- Run PAskit from the Desktop shortcut\n"
            "- Enter your activation code to get started"
        )
        self.finish_message.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(self.finish_message)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        finish_btn = QPushButton("Finish")
        finish_btn.setMinimumWidth(100)
        finish_btn.clicked.connect(self.close)
        button_layout.addWidget(finish_btn)

        layout.addLayout(button_layout)
        return page

    def browse_directory(self):
        """Browse for installation directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            str(self.install_dir.parent)
        )
        if directory:
            self.dir_input.setText(directory)

    def start_installation(self):
        """Start installation process."""
        install_dir = Path(self.dir_input.text())
        create_shortcuts = self.shortcuts_check.isChecked() or self.desktop_check.isChecked()

        # Check if source files exist
        if not self.source_dir.exists():
            QMessageBox.critical(
                self,
                "Error",
                f"Source files not found at:\n{self.source_dir}\n\n"
                "Please ensure the installer files are in the correct location."
            )
            return

        # Switch to progress page
        self.stacked_widget.setCurrentWidget(self.progress_page)

        # Start installation thread
        self.install_thread = InstallThread(self.source_dir, install_dir, create_shortcuts)
        self.install_thread.progress.connect(self.update_progress)
        self.install_thread.status.connect(self.update_status)
        self.install_thread.finished.connect(self.installation_finished)
        self.install_thread.start()

    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def update_status(self, status):
        """Update status label."""
        self.status_label.setText(status)

    def installation_finished(self, success):
        """Handle installation completion."""
        if success:
            self.stacked_widget.setCurrentWidget(self.finish_page)
        else:
            QMessageBox.critical(
                self,
                "Installation Failed",
                "An error occurred during installation.\n\n"
                "Please check the status message for details."
            )
            self.stacked_widget.setCurrentWidget(self.install_page)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    installer = PaskitInstaller()
    installer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
