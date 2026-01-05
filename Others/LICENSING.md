"""
PAskit Licensing System Documentation

## Overview

PAskit uses a cryptographic licensing system based on HMAC-SHA256 signatures.
Activation codes are generated offline and validated locally without requiring
internet connection.

## How It Works

### 1. Code Generation
- Administrator generates activation codes using `generate_activation_code.py`
- Each code contains encrypted user information (name, email, expiry date)
- Code is signed with HMAC-SHA256 to prevent forgery
- Codes are formatted as: XXXX-XXXX-XXXX-... for readability

### 2. Code Validation
- User enters activation code in the activation dialog
- Application validates the signature using embedded master key
- If signature is valid and not expired, license is activated
- License is saved to: ~/.paskit/licenses/license.json

### 3. License Persistence
- Once activated, license is stored locally
- Application checks for valid license on startup
- If valid license exists, user bypasses activation dialog
- If license expires or is invalid, activation dialog appears again

## Security Features

### Cryptographic Signing
- Uses HMAC-SHA256 for code signing
- Master key is embedded in the application
- Codes cannot be forged without the master key
- Signature verification prevents tampering

### No Internet Required
- All validation happens locally
- No server connection needed
- Works offline completely
- Codes are self-contained and self-validating

### Expiry Support
- Codes can have optional expiry dates
- Perpetual licenses supported (no expiry)
- Expired licenses are rejected with clear error message

## Usage

### For Administrators

#### Generate a 1-year license:
```bash
python generate_activation_code.py --name "John Doe" --email "john@example.com" --days 365
```

#### Generate a perpetual license:
```bash
python generate_activation_code.py --name "Jane Smith" --email "jane@example.com" --perpetual
```

#### Generate and save to file:
```bash
python generate_activation_code.py --name "Team License" --email "team@company.com" --output licenses.txt
```

### For Users

1. Run the application: `python run.py`
2. Activation dialog appears (if no valid license)
3. Paste the activation code
4. Click "Activate"
5. Application starts after successful activation

## File Locations

- **License Storage:** `~/.paskit/licenses/license.json`
- **Code Generator:** `generate_activation_code.py` (in project root)
- **License Manager:** `src/licensing/license_manager.py`
- **Activation Dialog:** `src/gui/activation_dialog.py`

## License File Format

```json
{
  "code": "XXXX-XXXX-XXXX-...",
  "license_data": {
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "issued_date": "2024-01-03T10:30:00.000000",
    "expiry_date": "2025-01-03T10:30:00.000000",
    "features": ["all"]
  },
  "activated_date": "2024-01-03T10:35:00.000000"
}
```

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid code format" | Code is corrupted or malformed | Verify code was copied correctly |
| "Invalid code signature - code may be forged" | Code signature doesn't match | Code may be tampered with, get new code |
| "License has expired" | License expiry date has passed | Contact support for renewal |
| "No license found" | First run or license file deleted | Enter activation code |

## Troubleshooting

### License file corrupted
- Delete: `~/.paskit/licenses/license.json`
- Restart application
- Re-enter activation code

### Forgot activation code
- Contact support at support@paskit.ai
- Provide name and email used for license

### Need to transfer license
- Delete license file on old machine
- Use same activation code on new machine
- Codes can be reused on multiple machines

## Technical Details

### Master Key
- Embedded in: `src/licensing/license_manager.py`
- Used for HMAC-SHA256 signing
- Should be kept secure in production

### Validation Process
1. Remove formatting from code (hyphens, spaces)
2. Decode from base64
3. Parse JSON to extract data and signature
4. Verify HMAC-SHA256 signature
5. Check expiry date if present
6. Return validation result

### Code Format
- Base64 encoded JSON
- Contains license data and HMAC signature
- Formatted with hyphens for readability
- Self-contained (no external validation needed)
"""
