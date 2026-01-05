#!/usr/bin/env python3
"""
Installer Generator for PAskit.

Creates Windows installer (EXE) using NSIS.
Requires NSIS to be installed on the system.

Installation:
    Download NSIS from: https://nsis.sourceforge.io/
    Or install via: choco install nsis
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def find_nsis():
    """Find NSIS installation directory."""
    possible_paths = [
        r"C:\Program Files (x86)\NSIS",
        r"C:\Program Files\NSIS",
        r"C:\NSIS",
    ]

    for path in possible_paths:
        makensis = Path(path) / "makensis.exe"
        if makensis.exists():
            return makensis

    return None


def main():
    """Generate installer."""
    print("\n" + "=" * 70)
    print("PAskit Installer Generator")
    print("=" * 70)

    # Get project root
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    exe_file = dist_dir / "PAskit.exe"
    nsi_file = project_root / "installer.nsi"

    # Check if executable exists
    if not exe_file.exists():
        print("\nError: PAskit.exe not found!")
        print("Please run 'python build.py' first to create the executable.")
        return 1

    print(f"\n[1/3] Checking prerequisites...")
    print(f"  Found executable: {exe_file}")

    # Check if NSIS is installed
    makensis = find_nsis()
    if not makensis:
        print("\n[2/3] NSIS not found!")
        print("\nTo create an installer, you need to install NSIS:")
        print("  1. Download from: https://nsis.sourceforge.io/")
        print("  2. Or install via: choco install nsis")
        print("  3. Then run this script again")
        print("\nAlternatively, you can use the ZIP distribution:")
        print(f"  {project_root / 'release' / 'PAskit-release.zip'}")
        return 1

    print(f"  Found NSIS: {makensis}")

    # Check if NSI file exists
    if not nsi_file.exists():
        print(f"\nError: {nsi_file} not found!")
        return 1

    print(f"  Found installer script: {nsi_file}")

    # Create output directory
    print(f"\n[2/3] Preparing installer...")
    release_dir = project_root / "release"
    release_dir.mkdir(parents=True, exist_ok=True)

    # Run NSIS compiler
    print(f"\n[3/3] Compiling installer...")
    output_file = release_dir / "PAskit-installer.exe"

    cmd = [
        str(makensis),
        f"/DOUTFILE={output_file}",
        str(nsi_file),
    ]

    try:
        result = subprocess.run(cmd, cwd=project_root, check=True, capture_output=True, text=True)
        print("  Installer compiled successfully!")
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e}")
        print(f"  Output: {e.stdout}")
        print(f"  Error: {e.stderr}")
        return 1

    # Verify output
    if output_file.exists():
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"\n  Installer size: {size_mb:.2f} MB")
    else:
        print(f"\nError: Installer not created!")
        return 1

    print("\n" + "=" * 70)
    print("Installer created successfully!")
    print("=" * 70)
    print(f"\nInstaller location: {output_file}")
    print("\nNext steps:")
    print("1. Test the installer on a Windows machine")
    print("2. Distribute PAskit-installer.exe to users")
    print("3. Users can run the installer to install PAskit")
    print("\nInstaller features:")
    print("  - Installs to Program Files")
    print("  - Creates Start Menu shortcuts")
    print("  - Creates Desktop shortcut")
    print("  - Includes uninstaller")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
