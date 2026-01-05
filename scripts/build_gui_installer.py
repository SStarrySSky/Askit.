#!/usr/bin/env python3
"""
Build GUI Installer Executable

Converts the Python GUI installer into a standalone EXE file.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Build GUI installer executable."""
    print("\n" + "=" * 70)
    print("PAskit GUI Installer Builder")
    print("=" * 70)

    # Get project root (go up one level from scripts folder)
    project_root = Path(__file__).parent.parent
    gui_installer = project_root / "scripts" / "gui_installer.py"
    dist_dir = project_root / "dist"
    release_dir = project_root / "release"

    # Check if gui_installer.py exists
    if not gui_installer.exists():
        print("\nError: gui_installer.py not found!")
        return 1

    print(f"\n[1/3] Checking prerequisites...")
    print(f"  Found: {gui_installer.name}")

    # Build with PyInstaller
    print(f"\n[2/3] Building GUI installer executable...")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=PAskit-Setup",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico",
        "--add-data=release/PAskit-Installer:release/PAskit-Installer",
        str(gui_installer),
    ]

    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print("  Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"  Build failed: {e}")
        return 1

    # Check output
    print(f"\n[3/3] Verifying output...")
    exe_file = dist_dir / "PAskit-Setup.exe"

    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"  Created: {exe_file.name}")
        print(f"  Size: {size_mb:.2f} MB")

        # Copy to release directory
        import shutil
        release_exe = release_dir / "PAskit-Setup.exe"
        shutil.copy(exe_file, release_exe)
        print(f"  Copied to: {release_exe}")
    else:
        print(f"  Error: {exe_file.name} not created!")
        return 1

    print("\n" + "=" * 70)
    print("GUI Installer built successfully!")
    print("=" * 70)
    print(f"\nInstaller location: {release_exe}")
    print("\nNext steps:")
    print("1. Run: PAskit-Setup.exe")
    print("2. Follow the installation wizard")
    print("3. Complete the installation")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
