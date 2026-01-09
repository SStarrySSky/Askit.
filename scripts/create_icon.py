#!/usr/bin/env python3
"""
Create application icon using Pillow.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_icon(output_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Create icon with 'A' and star."""
    print(f"Creating icon at {output_path}...")

    # Create images at different sizes
    images = []

    for size in sizes:
        # Create image with transparency
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw background circle with gradient effect
        # Use blue color scheme
        for i in range(size // 2):
            alpha = int(255 * (1 - i / (size / 2)))
            color = (74, 144, 226, alpha)
            draw.ellipse(
                [i, i, size - i, size - i],
                fill=(74, 144, 226, 255),
                outline=None
            )

        # Draw letter 'A'
        # Calculate font size based on icon size
        font_size = int(size * 0.6)

        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()

        # Draw 'A' in center
        text = "A"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - int(size * 0.05)

        # Draw text with white color
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

        # Draw Gemini cross star in upper right
        star_size = int(size * 0.15)
        star_x = int(size * 0.75)
        star_y = int(size * 0.25)

        # Draw four-pointed star
        star_points = [
            (star_x, star_y - star_size),  # top
            (star_x - star_size // 3, star_y - star_size // 3),
            (star_x - star_size, star_y),  # left
            (star_x - star_size // 3, star_y + star_size // 3),
            (star_x, star_y + star_size),  # bottom
            (star_x + star_size // 3, star_y + star_size // 3),
            (star_x + star_size, star_y),  # right
            (star_x + star_size // 3, star_y - star_size // 3),
        ]
        draw.polygon(star_points, fill=(255, 215, 0, 255), outline=(255, 165, 0, 255))

        # Draw center sparkle
        sparkle_size = max(2, star_size // 5)
        draw.ellipse(
            [star_x - sparkle_size, star_y - sparkle_size,
             star_x + sparkle_size, star_y + sparkle_size],
            fill=(255, 255, 255, 200)
        )

        images.append(img)

    # Save as ICO with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    print(f"Created: {output_path.name}")
    print(f"  Sizes: {', '.join(f'{s}x{s}' for s in sizes)}")


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "assets"
    assets_dir.mkdir(exist_ok=True)

    ico_path = assets_dir / "icon.ico"
    png_path = assets_dir / "icon.png"

    # Create ICO file
    create_icon(ico_path)

    # Also create a 256x256 PNG for other uses
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw background circle
    draw.ellipse([10, 10, 246, 246], fill=(74, 144, 226, 255))

    # Draw 'A'
    try:
        font = ImageFont.truetype("arial.ttf", 150)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "A", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - 10

    draw.text((x, y), "A", fill=(255, 255, 255, 255), font=font)

    # Draw star
    star_size = 38
    star_x = 190
    star_y = 65
    star_points = [
        (star_x, star_y - star_size),
        (star_x - star_size // 3, star_y - star_size // 3),
        (star_x - star_size, star_y),
        (star_x - star_size // 3, star_y + star_size // 3),
        (star_x, star_y + star_size),
        (star_x + star_size // 3, star_y + star_size // 3),
        (star_x + star_size, star_y),
        (star_x + star_size // 3, star_y - star_size // 3),
    ]
    draw.polygon(star_points, fill=(255, 215, 0, 255), outline=(255, 165, 0, 255))
    draw.ellipse([star_x - 7, star_y - 7, star_x + 7, star_y + 7], fill=(255, 255, 255, 200))

    img.save(png_path)
    print(f"Created: {png_path.name}")

    print(f"\nIcon creation completed!")
    print(f"Output files:")
    print(f"  - {ico_path}")
    print(f"  - {png_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
