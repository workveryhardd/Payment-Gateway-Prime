# How to Change UPI Details - Complete Guide

This guide shows you exactly how to update UPI ID, QR code, and other payment details.

## Quick Steps

### 1. Update UPI ID

**File:** `backend/app/assets/upi_details.txt`

**Current content:**
```
upi_id=yourupi@bank
payee_name=Your Business Name
```

**To change:**
1. Open the file: `backend/app/assets/upi_details.txt`
2. Change the `upi_id=` line to your new UPI ID
3. Change the `payee_name=` line to your business name
4. Save the file
5. **No restart needed!** Changes take effect immediately

**Example:**
```
upi_id=yournewupi@paytm
payee_name=Your Business Name
```

---

### 2. Update QR Code

**Location:** `backend/app/assets/qr.jpg`

**To change:**
1. Get your new QR code image (JPG or PNG format)
2. Name it `qr.jpg`
3. Replace the file at: `backend/app/assets/qr.jpg`
4. **No restart needed!** Changes take effect immediately

**Supported formats:**
- ✅ `.jpg` / `.jpeg`
- ✅ `.png`

**Note:** The file must be named `qr.jpg` (or update the code to use a different name)

---

### 3. Update Bank Details

**File:** `backend/app/assets/bank_details.txt`

**Current format:**
```
account_number=123456789012
ifsc=BANK0001234
bank_name=Bank Name
branch=Branch Name
```

**To change:**
1. Open the file: `backend/app/assets/bank_details.txt`
2. Update each line with your bank details
3. Save the file
4. **No restart needed!**

---

### 4. Update Crypto Wallets

**File:** `backend/app/assets/crypto_wallets.json`

**Current format:**
```json
{
  "btc": "bc1qexamplebtcaddress000000000000000000",
  "eth": "0xExampleEthereumAddress0000000000000000000000",
  "usdt_trc20": "TYExampleTronAddress0000000000000000",
  "usdt_erc20": "0xExampleERC20Address00000000000000000000",
  "usdt_bep20": "0xExampleBSCAddress000000000000000000000"
}
```

**To change:**
1. Open the file: `backend/app/assets/crypto_wallets.json`
2. Update the wallet addresses
3. Make sure JSON format is valid (use a JSON validator if needed)
4. Save the file
5. **No restart needed!**

---

## How It Works

### Backend API Endpoint

The backend has an endpoint that reads these files:

**Endpoint:** `GET /payment/payment-instructions`

**Response:**
```json
{
  "upi": {
    "id": "yourupi@bank",
    "name": "Your Business Name"
  },
  "bank": {
    "account": "123456789012",
    "ifsc": "BANK0001234",
    "bank": "Bank Name",
    "branch": "Branch Name"
  },
  "crypto": {
    "btc": "...",
    "eth": "...",
    ...
  }
}
```

**QR Code Endpoint:** `GET /payment/qr-code`
- Returns the QR code image
- Automatically serves `backend/app/assets/qr.jpg`

### Frontend

The frontend fetches this data when you create a deposit:
- Calls `/payment/payment-instructions` API
- Displays UPI ID, bank details, crypto addresses
- Shows QR code image from `/payment/qr-code`

---

## Step-by-Step: Changing UPI ID

### Method 1: Using Text Editor

1. **Navigate to backend folder:**
   ```bash
   cd backend/app/assets
   ```

2. **Open `upi_details.txt` in any text editor:**
   - Notepad (Windows)
   - TextEdit (Mac)
   - VS Code
   - Any text editor

3. **Edit the file:**
   ```
   upi_id=yournewupi@paytm
   payee_name=Your Business Name
   ```

4. **Save the file**

5. **Test it:**
   - Go to frontend: http://localhost:5173
   - Create a deposit with UPI method
   - Check if new UPI ID is displayed

### Method 2: Using Command Line

**Windows PowerShell:**
```powershell
cd backend\app\assets
notepad upi_details.txt
# Edit and save in Notepad
```

**Linux/Mac:**
```bash
cd backend/app/assets
nano upi_details.txt
# Edit, then press Ctrl+X, Y, Enter to save
```

---

## Step-by-Step: Changing QR Code

### Method 1: Replace File

1. **Get your QR code image:**
   - Generate from UPI app
   - Download from bank
   - Create using online QR generator

2. **Name it `qr.jpg`**

3. **Replace the file:**
   ```bash
   # Copy your new QR code to:
   backend/app/assets/qr.jpg
   ```

4. **Verify:**
   - Open: http://localhost:8000/payment/qr-code
   - Should show your new QR code

### Method 2: Using Command Line

**Windows:**
```powershell
# Copy your QR code file
Copy-Item "C:\path\to\your\qr.jpg" "backend\app\assets\qr.jpg" -Force
```

**Linux/Mac:**
```bash
# Copy your QR code file
cp /path/to/your/qr.jpg backend/app/assets/qr.jpg
```

---

## File Locations Summary

All payment-related files are in: `backend/app/assets/`

```
backend/app/assets/
├── upi_details.txt          # UPI ID and payee name
├── qr.jpg                   # UPI QR code image
├── bank_details.txt         # Bank account details
└── crypto_wallets.json      # Crypto wallet addresses
```

---

## Testing Changes

### Test UPI Details

1. **Check API directly:**
   ```bash
   # Open in browser or use curl
   http://localhost:8000/payment/payment-instructions
   ```

2. **Check in frontend:**
   - Go to: http://localhost:5173
   - Create a deposit
   - Select UPI method
   - Verify UPI ID is correct

### Test QR Code

1. **Check QR code endpoint:**
   ```bash
   # Open in browser
   http://localhost:8000/payment/qr-code
   ```

2. **Check in frontend:**
   - Create a UPI deposit
   - QR code should appear below UPI ID
   - Scan with UPI app to verify it works

---

## Troubleshooting

### Problem: Changes not showing

**Solution:**
- Make sure you saved the file
- Check file location is correct
- Restart the backend server if needed:
  ```bash
  # Stop server (Ctrl+C)
  # Start again
  uvicorn app.main:app --reload
  ```

### Problem: QR code not displaying

**Solution:**
1. Check file exists: `backend/app/assets/qr.jpg`
2. Check file format (should be JPG or PNG)
3. Check file size (not too large)
4. Check browser console for errors
5. Try accessing directly: http://localhost:8000/payment/qr-code

### Problem: Invalid JSON in crypto_wallets.json

**Solution:**
- Use a JSON validator: https://jsonlint.com/
- Make sure all quotes are double quotes
- Make sure there's a comma between entries (except last one)
- Make sure file ends with closing brace `}`

### Problem: UPI ID not updating

**Solution:**
1. Check file format:
   ```
   upi_id=yourupi@bank
   payee_name=Your Name
   ```
2. No spaces around `=`
3. One entry per line
4. File encoding should be UTF-8

---

## Best Practices

1. **Backup before changing:**
   ```bash
   # Copy original files
   cp upi_details.txt upi_details.txt.backup
   cp qr.jpg qr.jpg.backup
   ```

2. **Test after changes:**
   - Always test in browser
   - Verify QR code scans correctly
   - Check all payment methods

3. **Keep files organized:**
   - All payment files in `backend/app/assets/`
   - Use consistent naming
   - Document any custom changes

4. **Version control:**
   - Commit changes to git
   - Add comments in files if needed
   - Keep sensitive data out of git (use .env for secrets)

---

## Current Configuration

**UPI ID:** `yourupi@bank` (configure in upi_details.txt)  
**Payee Name:** `Your Business Name` (configure in upi_details.txt)  
**QR Code:** `backend/app/assets/qr.jpg` (add your QR code file)

---

## Quick Reference

| What to Change | File Location | Format |
|---------------|---------------|--------|
| UPI ID | `backend/app/assets/upi_details.txt` | `upi_id=xxx@bank` |
| QR Code | `backend/app/assets/qr.jpg` | JPG/PNG image |
| Bank Details | `backend/app/assets/bank_details.txt` | `key=value` format |
| Crypto Wallets | `backend/app/assets/crypto_wallets.json` | JSON format |

**That's it!** You can now change payment details anytime without touching code! 🎉

