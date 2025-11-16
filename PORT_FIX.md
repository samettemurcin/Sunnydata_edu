# Port Configuration Fix

## Issue
Port 5000 was being used by Apple AirPlay service on macOS, causing connection failures.

## Solution
Changed the backend server to use **port 5001** instead of port 5000.

## Changes Made

1. **Backend (`app.py`):**
   - Changed from `port=5000` to `port=5001`

2. **Frontend (`frontend/app.js`):**
   - Updated API_BASE_URL from `http://localhost:5000/api` to `http://localhost:5001/api`

## Verification

The backend is now running and accessible at:
- **Backend:** http://localhost:5001
- **Health Check:** http://localhost:5001/api/health
- **Status:** http://localhost:5001/api/status

## Testing

You can test the connection by running:
```bash
curl http://localhost:5001/api/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

## Frontend

The frontend at http://localhost:8000 should now connect successfully to the backend.

## If You Want to Use Port 5000

If you want to use port 5000, you'll need to disable AirPlay Receiver:
1. Go to System Settings > General > AirDrop & Handoff
2. Turn off "AirPlay Receiver"

However, using port 5001 is recommended as it avoids conflicts.

