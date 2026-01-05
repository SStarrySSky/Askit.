"""
License management system for PAskit.

Provides simple 16-character activation code generation and validation.
"""

import json
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger


class LicenseManager:
    """Manages license activation codes and validation."""

    # Valid activation codes storage (in production, use a database)
    # Format: {code: {"activated_date": "...", "machine_id": "..."}}
    VALID_CODES_FILE = Path.home() / ".paskit" / "licenses" / "valid_codes.json"

    # License storage location
    LICENSE_DIR = Path.home() / ".paskit" / "licenses"

    def __init__(self):
        """Initialize license manager."""
        self.LICENSE_DIR.mkdir(parents=True, exist_ok=True)
        self.license_file = self.LICENSE_DIR / "license.json"
        self._load_valid_codes()

    def _load_valid_codes(self):
        """Load valid codes from file."""
        if self.VALID_CODES_FILE.exists():
            try:
                with open(self.VALID_CODES_FILE, "r") as f:
                    self.valid_codes = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load valid codes: {e}")
                self.valid_codes = {}
        else:
            self.valid_codes = {}

    def _save_valid_codes(self):
        """Save valid codes to file."""
        try:
            self.VALID_CODES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.VALID_CODES_FILE, "w") as f:
                json.dump(self.valid_codes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save valid codes: {e}")

    @staticmethod
    def generate_activation_code() -> str:
        """
        Generate a simple 16-character activation code.

        Format: XXXX-XXXX-XXXX-XXXX (4 groups of 4 characters)

        Returns:
            Activation code string
        """
        # Use uppercase letters and digits
        chars = string.ascii_uppercase + string.digits

        # Generate 16 random characters
        code_chars = "".join(random.choice(chars) for _ in range(16))

        # Format as XXXX-XXXX-XXXX-XXXX
        code_formatted = "-".join(
            [code_chars[i : i + 4] for i in range(0, 16, 4)]
        )

        return code_formatted

    def add_valid_code(self, code: str) -> bool:
        """
        Add a valid activation code to the system.

        Args:
            code: Activation code to add

        Returns:
            True if added successfully
        """
        code_clean = code.replace("-", "").replace(" ", "").upper()

        if len(code_clean) != 16:
            logger.error(f"Invalid code length: {len(code_clean)}")
            return False

        self.valid_codes[code_clean] = {
            "created_date": datetime.now().isoformat(),
            "activated": False,
        }

        self._save_valid_codes()
        logger.info(f"Added valid code: {code_clean}")
        return True

    @staticmethod
    def validate_activation_code(code: str) -> Tuple[bool, str]:
        """
        Validate an activation code.

        Args:
            code: Activation code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        code_clean = code.replace("-", "").replace(" ", "").upper()

        # Check length
        if len(code_clean) != 16:
            return False, f"Invalid code length: {len(code_clean)} (expected 16)"

        # Check if all characters are alphanumeric
        if not code_clean.isalnum():
            return False, "Code contains invalid characters"

        return True, ""

    def save_license(self, code: str) -> Tuple[bool, str]:
        """
        Save activated license to disk.

        Args:
            code: Activation code

        Returns:
            Tuple of (success, message)
        """
        is_valid, error = self.validate_activation_code(code)

        if not is_valid:
            return False, error

        try:
            code_clean = code.replace("-", "").replace(" ", "").upper()

            license_info = {
                "code": code_clean,
                "activated_date": datetime.now().isoformat(),
            }

            with open(self.license_file, "w") as f:
                json.dump(license_info, f, indent=2)

            logger.info(f"[LicenseManager] License activated with code: {code_clean}")
            return True, "License activated successfully"

        except Exception as e:
            logger.error(f"[LicenseManager] Failed to save license: {e}")
            return False, f"Failed to save license: {str(e)}"

    def load_license(self) -> Tuple[bool, str]:
        """
        Load saved license from disk.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.license_file.exists():
            return False, "No license found"

        try:
            with open(self.license_file, "r") as f:
                license_info = json.load(f)

            code = license_info.get("code")
            if not code:
                return False, "Invalid license file"

            # Validate the stored code
            is_valid, error = self.validate_activation_code(code)

            if not is_valid:
                return False, error

            return True, ""

        except json.JSONDecodeError:
            return False, "Corrupted license file"
        except Exception as e:
            logger.error(f"[LicenseManager] Failed to load license: {e}")
            return False, f"Failed to load license: {str(e)}"

    def is_licensed(self) -> bool:
        """Check if application has valid license."""
        is_valid, _ = self.load_license()
        return is_valid

    def get_license_info(self) -> Optional[dict]:
        """Get current license information."""
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, "r") as f:
                return json.load(f)
        except Exception:
            return None
