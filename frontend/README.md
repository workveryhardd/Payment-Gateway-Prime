# Deposit System Frontend

A React + TypeScript frontend for the deposit system.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API URL

Create a `.env` file in the frontend directory:

```
VITE_API_BASE_URL=http://localhost:8000
```

If not set, it defaults to `http://localhost:8000`.

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/   # Reusable components
│   ├── pages/        # Page components
│   ├── lib/          # API and auth utilities
│   └── App.tsx       # Main app component
├── public/           # Static assets
└── package.json
```

## Features

- User authentication (login)
- Dashboard to view deposits
- Create deposits (UPI, Bank, Crypto)
- Submit payment proof (UTR/hash)
- Admin interface for managing deposits

