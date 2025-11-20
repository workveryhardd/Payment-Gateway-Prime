# Multi-Account Payment Feature

## Overview
This feature allows you to manage multiple payment accounts (UPI, Bank, Crypto) and switch between them dynamically. Only approved and activated accounts are shown to users when they make payments.

## Features

### 1. **Multiple Account Support**
   - Upload multiple UPI accounts
   - Upload multiple Bank accounts
   - Upload multiple Crypto wallet sets
   - Each account has a unique `identifier_name` (e.g., "id1", "main_bank", "backup_crypto")

### 2. **Admin Management**
   - **Upload JSON file** with all account details
   - **Approve/Reject** accounts (status: PENDING → ACTIVE/INACTIVE)
   - **Activate/Deactivate** accounts (only one active per type)
   - **Delete** accounts

### 3. **Automatic Display**
   - Only **active** accounts are shown to users during payment
   - When you activate a new account, the previous one is automatically deactivated
   - Users don't need to login to see payment instructions

## JSON File Format

Create a JSON file with this structure:

```json
{
  "upi": [
    {
      "identifier_name": "id1",
      "upi_id": "yourupi1@bank",
      "payee_name": "Business Account 1",
      "qr_location": "backend/app/assets/qr1.jpg"
    },
    {
      "identifier_name": "id2",
      "upi_id": "yourupi2@bank",
      "payee_name": "Business Account 2",
      "qr_location": "backend/app/assets/qr2.jpg"
    }
  ],
  "bank": [
    {
      "identifier_name": "main_bank",
      "account_number": "123456789012",
      "ifsc": "BANK0001234",
      "bank_name": "Bank Name",
      "branch": "Branch Name"
    }
  ],
  "crypto": [
    {
      "identifier_name": "main_crypto",
      "btc": "bc1qexamplebtcaddress000000000000000000",
      "eth": "0xExampleEthereumAddress0000000000000000000000",
      "usdt_trc20": "TYExampleTronAddress0000000000000000",
      "usdt_erc20": "0xExampleERC20Address00000000000000000000",
      "usdt_bep20": "0xExampleBSCAddress000000000000000000000"
    }
  ]
}
```

### Field Requirements

#### UPI Accounts
- `identifier_name` (required): Unique identifier like "id1", "main_upi"
- `upi_id` (required): UPI ID (e.g., "7703897896@ptsbi")
- `payee_name` (required): Name shown to payer
- `qr_location` (optional): Path to QR code image (relative to project root or absolute)

#### Bank Accounts
- `identifier_name` (required): Unique identifier
- `account_number` (required): Bank account number
- `ifsc` (required): IFSC code
- `bank_name` (required): Bank name
- `branch` (optional): Branch name

#### Crypto Accounts
- `identifier_name` (required): Unique identifier
- `btc` (optional): Bitcoin address
- `eth` (optional): Ethereum address
- `usdt_trc20` (optional): USDT on Tron
- `usdt_erc20` (optional): USDT on Ethereum
- `usdt_bep20` (optional): USDT on BSC

## How to Use

### Step 1: Upload Accounts
1. Go to **Admin → Payment Accounts** page
2. Click **"Upload JSON File"**
3. Select your JSON file with account details
4. Accounts will be created with status **PENDING**

### Step 2: Approve Accounts
1. Review uploaded accounts in the table
2. Click **"Approve"** for accounts you want to use
3. Status changes to **ACTIVE**

### Step 3: Activate Account
1. Click **"Activate"** on the account you want to display
2. This automatically deactivates other accounts of the same type
3. Only the active account is shown to users

### Step 4: Switch Accounts
- To switch to a different account:
  1. Approve the new account (if not already approved)
  2. Click **"Activate"** on the new account
  3. The old account is automatically deactivated

## API Endpoints

### Admin Endpoints (No auth required currently)

- `POST /admin/payment-accounts/upload` - Upload JSON file
- `GET /admin/payment-accounts/` - List all accounts
- `POST /admin/payment-accounts/{id}/approve` - Approve account
- `POST /admin/payment-accounts/{id}/reject` - Reject account
- `POST /admin/payment-accounts/{id}/activate` - Activate account
- `DELETE /admin/payment-accounts/{id}` - Delete account

### Public Endpoints (No login required)

- `GET /payment/payment-instructions` - Get active payment instructions
- `GET /payment/qr-code` - Get QR code from active UPI account

## Admin Credentials

- **Email:** vardiano@tech
- **Password:** Vardiano1
- Admin user is automatically created on server startup

## Example Workflow

1. **Upload multiple UPI accounts:**
   ```json
   {
     "upi": [
       {"identifier_name": "primary", "upi_id": "primary@bank", ...},
       {"identifier_name": "backup", "upi_id": "backup@bank", ...}
     ]
   }
   ```

2. **Approve both accounts** (they become ACTIVE)

3. **Activate "primary"** - Users see primary account

4. **Later, switch to "backup":**
   - Click "Activate" on backup account
   - Primary is automatically deactivated
   - Users now see backup account

## Notes

- Only **one account per type** can be active at a time
- Accounts must be **approved** before they can be activated
- **QR code location** can be:
  - Relative path from project root: `"backend/app/assets/qr.jpg"`
  - Absolute path: `"C:/path/to/qr.jpg"`
- If no active account exists, default values are shown
- All account details are stored as JSON in the database

