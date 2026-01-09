#!/usr/bin/env python3
"""
Competition Plan Activation Code Generator

Generates advanced activation codes for Competition Plan.
Format: COMP-XXXX-XXXX-XXXX (高级格式)
"""

import sys
import random
import string
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_competition_code():
    """Generate a Competition Plan activation code."""
    # Use uppercase letters and digits
    chars = string.ascii_uppercase + string.digits

    # Generate 12 random characters (after COMP- prefix)
    code_chars = "".join(random.choice(chars) for _ in range(12))

    # Format as COMP-XXXX-XXXX-XXXX
    code_formatted = f"COMP-{code_chars[0:4]}-{code_chars[4:8]}-{code_chars[8:12]}"

    return code_formatted


def main():
    """Generate Competition Plan activation codes."""
    print("\n" + "=" * 70)
    print("PAskit Competition Plan - Activation Code Generator")
    print("=" * 70)
    print("\nFormat: COMP-XXXX-XXXX-XXXX (高级格式)")
    print("Plan: Competition Edition")
    print("Features: Team activation, Advanced features")
    print("-" * 70)

    # Ask user how many codes to generate
    while True:
        try:
            count_input = input("\nHow many activation codes do you want to generate? ")
            count = int(count_input.strip())

            if count <= 0:
                print("Please enter a positive number.")
                continue

            if count > 1000:
                print("Maximum 1000 codes at a time.")
                continue

            break
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nGenerating {count} Competition Plan activation code(s)...\n")

    codes = []
    for i in range(count):
        code = generate_competition_code()
        codes.append(code)
        print(code)

    # Ask if user wants to save to file
    print("\n" + "-" * 70)
    save_choice = input("Do you want to save these codes to a file? (y/n): ").strip().lower()

    if save_choice == "y":
        while True:
            filename = input("Enter filename (default: competition_activation_codes.txt): ").strip()
            if not filename:
                filename = "competition_activation_codes.txt"

            try:
                with open(filename, "a") as f:
                    for code in codes:
                        f.write(f"{code}\n")

                print(f"\nCodes saved to: {filename}")
                break
            except Exception as e:
                print(f"Error saving to file: {e}")
                print("Please try again with a different filename.")

    print("\n" + "=" * 70)
    print("Competition Plan Activation Codes Generated")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
