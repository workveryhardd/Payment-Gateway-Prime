# Payment Assets

This directory contains payment-related configuration files.

## Setup Instructions

1. **Copy example files:**
   ```bash
   cp upi_details.txt.example upi_details.txt
   cp bank_details.txt.example bank_details.txt  # if exists
   ```

2. **Edit `upi_details.txt`** with your actual UPI ID:
   ```
   upi_id=yourupi@bank
   payee_name=Your Business Name
   ```

3. **Add your QR code:**
   - Place your UPI QR code image as `qr.jpg` in this directory
   - Supported formats: JPG, PNG

## Files

- `upi_details.txt` - Your UPI ID and payee name (NOT in git)
- `upi_details.txt.example` - Example template (in git)
- `qr.jpg` - Your UPI QR code image (NOT in git)
- `bank_details.txt` - Bank account details (NOT in git)
- `crypto_wallets.json` - Crypto wallet addresses (in git, update with your addresses)

**Note:** Actual payment details are excluded from git for security. Only example files are committed.

