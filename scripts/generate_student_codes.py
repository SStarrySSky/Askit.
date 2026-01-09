#!/usr/bin/env python3
"""
Student Plan Activation Code Generator

Generates simple 16-character activation codes for Student Plan.
Format: XXXX-XXXX-XXXX-XXXX
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.licensing import LicenseManager


def main():
    """Generate Student Plan activation codes."""
    print("\n" + "=" * 70)
    print("PAskit Student Plan - Activation Code Generator")
    print("=" * 70)
    print("\nFormat: XXXX-XXXX-XXXX-XXXX (16 characters)")
    print("Plan: Student Edition")
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

    print(f"\nGenerating {count} Student Plan activation code(s)...\n")

    codes = []
    for i in range(count):
        code = LicenseManager.generate_activation_code()
        codes.append(code)
        print(code)

    # Ask if user wants to save to file
    print("\n" + "-" * 70)
    save_choice = input("Do you want to save these codes to a file? (y/n): ").strip().lower()

    if save_choice == "y":
        while True:
            filename = input("Enter filename (default: student_activation_codes.txt): ").strip()
            if not filename:
                filename = "student_activation_codes.txt"

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
    print("Student Plan Activation Codes Generated")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
