#!/usr/bin/env python3
"""
Simple MSI Installer Generator for PAskit.

Creates a basic Windows installer without requiring NSIS.
Uses Python's built-in msilib module.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def create_simple_installer():
    """Create a simple installer package."""

    print("\n" + "=" * 70)
    print("PAskit Installer Generator (No NSIS Required)")
    print("=" * 70)

    # Get project root
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    exe_file = dist_dir / "PAskit.exe"
    release_dir = project_root / "release"

    # Check if executable exists
    if not exe_file.exists():
        print("\nError: PAskit.exe not found!")
        print("Please run 'python build.py' first to create the executable.")
        return 1

    print(f"\n[1/3] Checking prerequisites...")
    print(f"  Found executable: {exe_file}")
    print(f"  File size: {exe_file.stat().st_size / (1024*1024):.2f} MB")

    # Create release directory
    release_dir.mkdir(parents=True, exist_ok=True)

    # Create installer package
    print(f"\n[2/3] Creating installer package...")

    installer_dir = release_dir / "PAskit-Installer"
    installer_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    import shutil

    files_to_copy = [
        ("dist/PAskit.exe", "PAskit.exe"),
        ("README.md", "README.md"),
        ("LICENSING.md", "LICENSING.md"),
        ("generate_activation_code.py", "generate_activation_code.py"),
    ]

    for src, dst in files_to_copy:
        src_path = project_root / src
        dst_path = installer_dir / dst
        if src_path.exists():
            shutil.copy(src_path, dst_path)
            print(f"  Copied: {dst}")

    # Create installation batch script
    print(f"\n[3/3] Creating installation scripts...")

    install_bat = installer_dir / "install.bat"
    with open(install_bat, "w", encoding="utf-8") as f:
        f.write("""@echo off
REM PAskit Installation Script
REM Run this script to install PAskit

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo PAskit Installation
echo ======================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as Administrator!
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Set installation directory
set INSTALL_DIR=%ProgramFiles%\\PAskit
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Installing to: %INSTALL_DIR%
echo.

REM Copy files
echo Copying files...
copy "PAskit.exe" "%INSTALL_DIR%\\" >nul
copy "README.md" "%INSTALL_DIR%\\" >nul
copy "LICENSING.md" "%INSTALL_DIR%\\" >nul
copy "generate_activation_code.py" "%INSTALL_DIR%\\" >nul

REM Create shortcuts
echo Creating shortcuts...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PAskit.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\PAskit.exe'; $Shortcut.Save()"

REM Create desktop shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\PAskit.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\PAskit.exe'; $Shortcut.Save()"

echo.
echo ======================================================================
echo Installation completed successfully!
echo ======================================================================
echo.
echo PAskit has been installed to: %INSTALL_DIR%
echo.
echo You can now:
echo - Run PAskit from the Start Menu
echo - Run PAskit from the Desktop shortcut
echo - Run PAskit.exe directly from: %INSTALL_DIR%
echo.
pause
""")

    # Create uninstall batch script
    uninstall_bat = installer_dir / "uninstall.bat"
    with open(uninstall_bat, "w", encoding="utf-8") as f:
        f.write("""@echo off
REM PAskit Uninstallation Script

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo PAskit Uninstallation
echo ======================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as Administrator!
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

set INSTALL_DIR=%ProgramFiles%\\PAskit

if not exist "%INSTALL_DIR%" (
    echo PAskit is not installed.
    pause
    exit /b 1
)

echo Uninstalling from: %INSTALL_DIR%
echo.

REM Remove shortcuts
echo Removing shortcuts...
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PAskit.lnk" 2>nul
del "%USERPROFILE%\\Desktop\\PAskit.lnk" 2>nul

REM Remove files
echo Removing files...
rmdir /s /q "%INSTALL_DIR%"

echo.
echo ======================================================================
echo Uninstallation completed successfully!
echo ======================================================================
echo.
pause
""")

    # Create README for installer
    readme = installer_dir / "INSTALL_INSTRUCTIONS.txt"
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""PAskit Installation Instructions
================================

Method 1: Automatic Installation (Recommended)
----------------------------------------------
1. Right-click on "install.bat"
2. Select "Run as Administrator"
3. Follow the prompts
4. Installation will complete automatically

Method 2: Manual Installation
-----------------------------
1. Create a folder: C:\\Program Files\\PAskit
2. Copy all files from this folder to C:\\Program Files\\PAskit
3. Create shortcuts manually if desired

Method 3: Portable (No Installation)
------------------------------------
1. Simply run PAskit.exe from any location
2. No installation required
3. No registry changes

Uninstallation
--------------
1. Right-click on "uninstall.bat"
2. Select "Run as Administrator"
3. Confirm the uninstallation

System Requirements
-------------------
- Windows 7 or later
- 4GB RAM minimum
- 500MB disk space

Activation
----------
1. Run PAskit.exe
2. Enter your 16-character activation code
3. Click "Activate"
4. Start using PAskit!

For more information, see:
- README.md - General information
- LICENSING.md - License information

Support
-------
For issues or questions, please contact support.
""")

    # Create ZIP archive
    print(f"\n  Creating ZIP archive...")
    import zipfile

    zip_file = release_dir / "PAskit-installer.zip"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in installer_dir.glob("*"):
            zf.write(file, arcname=file.name)

    print(f"  Created: {zip_file.name}")

    # Summary
    print("\n" + "=" * 70)
    print("Installer created successfully!")
    print("=" * 70)
    print(f"\nInstaller location: {installer_dir}")
    print(f"ZIP archive: {zip_file}")
    print(f"\nFiles included:")
    for file in sorted(installer_dir.glob("*")):
        size = file.stat().st_size
        if size > 1024*1024:
            size_str = f"{size / (1024*1024):.2f} MB"
        else:
            size_str = f"{size / 1024:.2f} KB"
        print(f"  - {file.name} ({size_str})")

    print("\n" + "=" * 70)
    print("Installation Methods:")
    print("=" * 70)
    print("\n1. Automatic Installation:")
    print("   - Right-click install.bat")
    print("   - Select 'Run as Administrator'")
    print("   - Follow prompts")
    print("\n2. Manual Installation:")
    print("   - Copy files to C:\\Program Files\\PAskit")
    print("   - Create shortcuts manually")
    print("\n3. Portable (No Installation):")
    print("   - Run PAskit.exe directly")
    print("   - No installation required")
    print("\n" + "=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(create_simple_installer())
