# Licensing Assistant

A simple end-to-end scaffold with a Flask backend and React (Vite) frontend.

## Prerequisites
- Python 3.10+
- Node.js 18+

## Backend (Flask)
1. Create virtualenv and install deps:
   - Windows PowerShell:
     ```powershell
     cd backend
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```
2. Run the server:
   ```powershell
   python run.py
   ```
   - Server runs on `http://localhost:5000`
   - Health check: `http://localhost:5000/api/health`

## Frontend (React + Vite)
1. Install deps:
   ```powershell
   cd frontend
   npm install
   ```
2. Run dev server:
   ```powershell
   npm run dev
   ```
   - App runs on `http://localhost:5173`
   - Vite proxy forwards `/api` to backend at `http://localhost:5000`

## Configuration
- Backend env (`backend/.env`):
  - `PORT=5000`
  - `CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`
- Frontend env (`frontend/.env` optional):
  - `VITE_API_BASE=http://localhost:5000/api`

## Notes
- CORS is restricted to local dev origins.
- Keep secrets out of source control.
