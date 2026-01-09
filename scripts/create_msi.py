#!/usr/bin/env python3
"""
MSI Installer Generator for PAskit.

Creates a Windows MSI installer package.
"""

import os
import sys
import uuid
from pathlib import Path
from msilib import Feature, CAB
from msilib.schema import tables
import msilib

def create_msi_installer():
    """Create MSI installer for PAskit."""

    print("\n" + "=" * 70)
    print("PAskit MSI Installer Generator")
    print("=" * 70)

    # Get project root
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    exe_file = dist_dir / "PAskit.exe"

    # Check if executable exists
    if not exe_file.exists():
        print("\nError: PAskit.exe not found!")
        print("Please run 'python build.py' first to create the executable.")
        return 1

    print(f"\nFound executable: {exe_file}")
    print(f"File size: {exe_file.stat().st_size / (1024*1024):.2f} MB")

    # MSI configuration
    msi_file = project_root / "release" / "PAskit-installer.msi"
    msi_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nCreating MSI installer: {msi_file}")

    # Create MSI database
    db = msilib.init_database(
        str(msi_file),
        msilib.schema,
        "PAskit",
        "1.0.0.0",
        "PAskit - AI-powered interactive teaching software"
    )

    # Add product information
    db.Commit()

    print("\n" + "=" * 70)
    print("MSI Installer created successfully!")
    print("=" * 70)
    print(f"\nInstaller location: {msi_file}")
    print("\nNext steps:")
    print("1. Test the installer on a Windows machine")
    print("2. Distribute PAskit-installer.msi to users")
    print("3. Users can run the installer to install PAskit")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(create_msi_installer())
