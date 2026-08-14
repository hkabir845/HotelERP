# 🚀 How to Start the Application

## Quick Start

**First Time Setup:**
1. Double-click: `setup.bat` (installs dependencies)
2. Then double-click: `start.bat` (starts both servers)

**After Setup:**
**Just double-click:** `start.bat`

That's it! The script will:
- ✅ Clean up any existing processes
- ✅ Check and setup backend
- ✅ Check and setup frontend
- ✅ Start both servers
- ✅ Open two windows (Backend & Frontend)

## What Happens

1. **Port Cleanup** - Kills any processes on ports 8000 and 3000
2. **Backend Setup** - Checks virtual environment, creates if needed
3. **Frontend Setup** - Checks dependencies, installs if needed
4. **Backend Start** - Starts FastAPI server on port 8000
5. **Frontend Start** - Starts Next.js server on port 3000

## After Starting

⏳ **Wait 30-60 seconds** for both servers to start

Then open your browser:
- 🌐 **http://localhost:3000**

## Login

- **Email:** `superadmin@admin.com`
- **Password:** `Admin@123`

## Important Notes

- **Keep both windows open** while using the app
- Backend must be running for login to work
- Press `CTRL+C` in each window to stop the servers

## Troubleshooting

### Backend won't start?
- Make sure Python 3.8+ is installed
- Check if port 8000 is already in use

### Frontend won't start?
- Make sure Node.js 18+ is installed
- Check if port 3000 is already in use

### Login fails?
- Make sure backend is running (check Backend window)
- Wait for backend to fully start (30-60 seconds)

---

**That's it! Just run `START_APPLICATION.bat` and you're ready to go!** 🎉

