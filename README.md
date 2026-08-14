# Hotel & Resort Management ERP

World-Class Professional Hotel & Resort Management System - Multi-Tenant SaaS

## Quick Start

### First Time Setup

1. **Run setup script:**
   ```bash
   setup.bat
   ```
   This will:
   - Create Python virtual environment
   - Install backend dependencies
   - Initialize database
   - Install frontend dependencies

### Start the Application

**Run the start script:**
```bash
start.bat
```

This will:
- Start Backend server (Django) on http://127.0.0.1:8000
- Start Frontend server (Next.js) on http://localhost:3000
- Open the application in your browser

## Access Points

- **Frontend App:** http://localhost:3000/
- **Backend API:** http://127.0.0.1:8000/api/
- **Django Admin:** http://127.0.0.1:8000/admin/

## Login Credentials

- **Email:** superadmin@admin.com
- **Password:** Admin@123

## Technology Stack

### Backend
- **Framework:** Django + Django REST Framework (Python)
- **Database:** SQLite
- **ORM:** Django ORM
- **Authentication:** JWT (JSON Web Tokens)

### Frontend
- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand

## Project Structure

```
HotelERP/
├── backend/          # Django backend
│   ├── api/          # Django app (models, views, auth)
│   ├── hotel_erp/    # Project settings
│   ├── scripts/      # Legacy seed scripts
│   └── venv/         # Virtual environment
├── frontend/         # Next.js frontend
│   ├── app/         # Next.js app directory
│   ├── components/   # React components
│   └── lib/         # Utilities and API client
├── setup.bat         # Initial setup script
└── start.bat         # Start both servers
```

## Manual Setup (Alternative)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize database:
   ```bash
   python manage.py init_db
   ```

6. Start server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Features

- ✅ Multi-tenant SaaS architecture
- ✅ User authentication & authorization
- ✅ Frontdesk management
- ✅ Housekeeping
- ✅ Food & Beverage (F&B)
- ✅ Accounting system
- ✅ Asset & Maintenance
- ✅ Broadcast messaging
- ✅ Utilities
- ✅ Report Center

## Development

### Backend Development

- Django admin: http://127.0.0.1:8000/admin/
- Server runs with auto-reload when using runserver
- Database: SQLite (hotel_erp.db)

### Frontend Development

- Development server: http://localhost:3000
- Hot reload enabled
- TypeScript for type safety

## Troubleshooting

### Backend won't start?
- Make sure Python 3.8+ is installed
- Check if port 8000 is available
- Verify virtual environment is activated

### Frontend won't start?
- Make sure Node.js 18+ is installed
- Check if port 3000 is available
- Delete `.next` folder and try again

### Login fails?
- Make sure backend is running
- Wait 30-60 seconds after starting backend
- Check backend window for errors

## License

Private - All Rights Reserved

