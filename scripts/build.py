#!/usr/bin/env python3
"""
Build script for PAskit - creates standalone executable.

Usage:
    python build.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Build PAskit executable."""
    print("=" * 70)
    print("PAskit Build Script")
    print("=" * 70)

    # Get project root (go up one level from scripts folder)
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    # Clean previous builds
    print("\n[1/4] Cleaning previous builds...")
    for directory in [dist_dir, build_dir]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"  Removed: {directory}")

    # Build with PyInstaller
    print("\n[2/4] Building executable with PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=PAskit",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--icon=assets/icon.ico",  # Application icon
        "--add-data=src/assets:src/assets",  # Include assets
        "--hidden-import=PyQt5",
        "--hidden-import=qasync",
        "--hidden-import=loguru",
        "--hidden-import=pydantic",
        "--hidden-import=numpy",
        "--hidden-import=scipy",
        "--hidden-import=OpenGL",
        "--hidden-import=manimlib",
        "--collect-data=manimlib",  # Include manimlib config files
        "run.py",
    ]

    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print("  Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"  Build failed: {e}")
        return 1

    # Create release package
    print("\n[3/4] Creating release package...")
    release_dir = project_root / "release" / "PAskit"

    # Clean release directory if it exists
    if release_dir.exists():
        shutil.rmtree(release_dir)
        print(f"  Cleaned: {release_dir}")

    release_dir.mkdir(parents=True, exist_ok=True)

    # Copy executable only (no docs, no activation code generator)
    exe_file = dist_dir / "PAskit.exe"
    if exe_file.exists():
        shutil.copy(exe_file, release_dir / "PAskit.exe")
        print(f"  Copied: PAskit.exe")

    # Create distribution archive
    print("\n[4/4] Creating distribution archive...")
    archive_path = project_root / "release" / "PAskit-release"
    shutil.make_archive(
        str(archive_path),
        "zip",
        str(project_root / "release"),
        "PAskit"
    )
    print(f"  Created: PAskit-release.zip")

    print("\n" + "=" * 70)
    print("Build completed successfully!")
    print("=" * 70)
    print(f"\nRelease package location: {release_dir}")
    print(f"Distribution archive: {archive_path}.zip")
    print("\nNext steps:")
    print("1. Test PAskit.exe on a clean Windows machine")
    print("2. Distribute PAskit-release.zip to users")
    print("3. Users extract and run PAskit.exe")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
