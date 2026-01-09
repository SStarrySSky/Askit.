#!/usr/bin/env python3
"""
Convert SVG icon to ICO format for Windows.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
    import cairosvg
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install: pip install pillow cairosvg")
    sys.exit(1)


def svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Convert SVG to ICO with multiple sizes."""
    print(f"Converting {svg_path.name} to ICO format...")

    # Convert SVG to PNG at largest size first
    png_data = cairosvg.svg2png(
        url=str(svg_path),
        output_width=256,
        output_height=256
    )

    # Open as PIL Image
    img = Image.open(io.BytesIO(png_data))

    # Create list of images at different sizes
    images = []
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)

    # Save as ICO
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    print(f"✓ Created: {ico_path.name}")
    print(f"  Sizes: {', '.join(f'{s}x{s}' for s in sizes)}")


def main():
    """Main conversion function."""
    import io

    project_root = Path(__file__).parent.parent
    svg_path = project_root / "assets" / "icon.svg"
    ico_path = project_root / "assets" / "icon.ico"

    if not svg_path.exists():
        print(f"Error: {svg_path} not found!")
        return 1

    svg_to_ico(svg_path, ico_path)

    print(f"\nIcon conversion completed!")
    print(f"Output: {ico_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
