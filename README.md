# 📚 Distributed Assessment Platform
**IITM: Modern Application Development II**

A scalable, distributed assessment platform built using Flask, SQLAlchemy, SQLite, Redis, and Celery with automated notifications, reporting, and data export capabilities.

## 🏗️ Project Structure

```
distributed-assessment-platform/
├── 📁 quiz-master-api/          # Flask REST API Backend
│   ├── 📁 app/
│   │   ├── 📁 api/              # REST API endpoints
│   │   │   ├── 📁 admin/        # Admin-only endpoints
│   │   │   ├── 📁 auth/         # Authentication endpoints
│   │   │   └── 📁 user/         # User endpoints
│   │   ├── 📁 common/           # Shared utilities
│   │   │   ├── config.py        # App configuration
│   │   │   ├── logger.py        # Logging setup
│   │   │   ├── reminder_service.py  # Daily reminder logic
│   │   │   └── report_service.py    # Monthly reports & CSV export
│   │   ├── 📁 models/           # Database models
│   │   │   ├── user.py          # User model
│   │   │   ├── quiz.py          # Quiz model
│   │   │   ├── notification.py  # Notification settings
│   │   │   └── ...              # Other models
│   │   ├── 📁 schemas/          # API request/response schemas
│   │   ├── celery_app.py        # Celery configuration
│   │   ├── celery_tasks.py      # Background tasks
│   │   └── extensions.py        # Flask extensions
│   ├── 📁 instance/             # Database files
│   ├── 📁 migrations/           # Database migrations
│   ├── 📁 exports/              # Generated CSV exports
│   ├── 📁 log/                  # Application logs
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Flask app entry point
│   └── start_system.sh          # System startup script
├── 📁 quiz-master-ui/           # Vue.js Frontend SPA
│   ├── 📁 src/
│   │   ├── 📁 components/       # Reusable Vue components
│   │   ├── 📁 pages/            # Application pages
│   │   │   ├── 📁 admin/        # Admin dashboard pages
│   │   │   └── 📁 user/         # User dashboard pages
│   │   ├── 📁 stores/           # Pinia state management
│   │   ├── 📁 router/           # Vue router configuration
│   │   └── 📁 layouts/          # Page layouts
│   ├── package.json             # Node.js dependencies
│   └── vite.config.ts           # Vite build configuration
├── 📁 .vscode/                  # VS Code configuration
├── CSV_EXPORT_IMPLEMENTATION.md # Detailed feature documentation
└── README.md                    # This file
```

## ✨ Key Features

### 🔄 **Automated Background Jobs**
- **Daily Reminders**: G-Chat styled email reminders for inactive users and new quizzes
- **Monthly Reports**: Comprehensive HTML activity reports with performance analytics
- **CSV Exports**: On-demand quiz data exports with detailed metrics

### 👥 **User Management**
- **Role-based Access**: Admin and Student roles with appropriate permissions
- **Authentication**: JWT-based secure authentication system
- **User Preferences**: Customizable reminder times and notification settings

### 📊 **Quiz System**
- **Dynamic Quiz Creation**: Admin can create quizzes with chapters and subjects
- **Real-time Scoring**: Automatic score calculation and tracking
- **Performance Analytics**: Detailed performance insights and rankings

### 🎯 **Advanced Features**
- **Multi-time Scheduling**: Support for user-specific reminder times
- **Export History**: Track and manage all data exports
- **Professional UI**: Bootstrap 5 with TypeScript support
- **Responsive Design**: Mobile-friendly interface

## 🚀 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js SPA    │◄──►│  Flask REST API │◄──►│   SQLite DB     │
│  (Frontend)     │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │  Celery Worker  │◄──►│  Redis Broker   │
                    │ (Background)    │    │ (Message Queue) │
                    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Celery Beat    │
                    │  (Scheduler)    │
                    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask with Flask-API
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **Background Jobs**: Celery with Redis broker
- **Email**: Flask-Mail with HTML templates
- **Migrations**: Flask-Migrate (Alembic)

### Frontend
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **Styling**: Bootstrap 5
- **State Management**: Pinia with persistence
- **Build Tool**: Vite
- **HTTP Client**: Axios

### Infrastructure
- **Message Broker**: Redis
- **Task Queue**: Celery Beat for scheduling
- **File Storage**: Local filesystem
- **Logging**: Python logging with file rotation

## 📋 Prerequisites

Before setting up the project, ensure you have:

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Redis Server** for message brokering
- **Git** for version control

### Install Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Start Redis
sudo service redis-server start
# OR
redis-server
```

## 🏃‍♂️ Quick Start Guide

### 1. Clone Repository
```bash
# HTTPS
git clone https://github.com/YOUR_USERNAME/distributed-assessment-platform.git

# SSH
git clone git@github.com:YOUR_USERNAME/distributed-assessment-platform.git

cd distributed-assessment-platform
```

### 2. Backend Setup
```bash
cd quiz-master-api

# Create virtual environment
python3 -m venv .env
source .env/bin/activate  # Linux/Mac
# OR
.env\Scripts\activate     # Windows

# Install dependencies
# pip freeze > requirements.txt

cd quiz-master-api
pip install -r requirements.txt

# Set up database
flask db upgrade

# Configure email (optional for notifications)
export IITM_EMAIL_USER="your-email@gmail.com"
export IITM_EMAIL_PASS="your-app-password"
```

### 3. Frontend Setup
```bash
cd quiz-master-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🚀 Running the Complete System

The system requires multiple processes to run simultaneously:

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: Celery Worker (Background Jobs)
```bash
cd quiz-master-api
source .env/bin/activate
celery -A app.celery_app worker --loglevel=info
```

### Terminal 3: Celery Beat (Task Scheduler)
```bash
cd quiz-master-api
source .env/bin/activate
celery -A app.celery_app beat --loglevel=info
```

### Terminal 4: Flask API Server
```bash
cd quiz-master-api
source .env/bin/activate
python run.py
```

### Terminal 5: Vue Development Server
```bash
cd quiz-master-ui
npm run dev
```

### 🎯 **One-Command Startup** (Alternative)
```bash
cd quiz-master-api
chmod +x start_system.sh
./start_system.sh
```

## 🌐 Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs

## 🔧 Environment Configuration

### Backend Environment Variables
```bash
# Email Configuration (optional)
export IITM_EMAIL_USER="your-email@gmail.com"
export IITM_EMAIL_PASS="your-app-password"

# Database Configuration (default: SQLite)
export DATABASE_URL="sqlite:///distributed-assessment-platform.db"

# Celery Configuration
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/1"
```

### For Windows Users
```powershell
setx IITM_EMAIL_USER "your-email@gmail.com"
setx IITM_EMAIL_PASS "your-app-password"
```

## 🛡️ Authentication & Security

- **JWT Tokens**: Secure API authentication
- **Role-based Access**: Admin and User permissions  
- **CORS Enabled**: Frontend-backend communication
- **Input Validation**: Request/response validation
- **SQL Injection Protection**: SQLAlchemy ORM

## 📊 Database Management

### Migration Commands
```bash
# Initialize migrations (one-time setup)
flask db init

# Create migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Check current migration status
flask db current
```

### SQLite3 Command Line
```bash
# Access database
sqlite3 instance/distributed-assessment-platform.db

# Common commands
.tables                    # List all tables
.schema table_name        # Show table structure
SELECT * FROM user;       # Query data
.exit                     # Exit
```

## 🎯 Key API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Admin Features
- `POST /api/admin/report/trigger-monthly-reports` - Manual report trigger
- `GET /api/admin/settings/` - Notification settings
- `POST /api/admin/quiz/create` - Create new quiz

### User Features
- `POST /api/user/export/trigger-csv-export` - Request CSV export
- `GET /api/user/export/my-exports` - View export history
- `GET /api/user/dashboard/stats` - Dashboard statistics

## 🔍 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   redis-cli ping
   # Should return: PONG
   ```

2. **Database Migration Issues**
   ```bash
   # Reset migrations (development only)
   rm -rf migrations/
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **Celery Worker Not Starting**
   ```bash
   # Check Celery configuration
   celery -A app.celery_app inspect stats
   ```

4. **Email Not Sending**
   - Verify email credentials are set
   - Check Gmail app password (not regular password)
   - Ensure less secure apps are enabled

## 📈 Monitoring & Logs

### Log Files
- **Flask App**: `app/log/app.log`

### Monitoring Commands
```bash
# Check running processes
ps aux | grep -E "(celery|redis|python)"

# Monitor Redis
redis-cli monitor

# Celery task monitoring
celery -A app.celery_app inspect active
```## 🧪 Testing & Development

### Demo Scripts
```bash
# Test monthly reports
python dev-tools/demo_monthly_reports.py

# Test CSV exports
python dev-tools/demo_csv_export.py

# Generate sample data
python dev-tools/generate_sample_report.py

# Test Redis cache functionality
python dev-tools/test_redis_cache.py

# Test Celery tasks
python dev-tools/test_celery_tasks.py
```

### Development Debugging
- **VS Code Configuration**: `.vscode/launch.json` included
- **Debug Mode**: Set `FLASK_ENV=development`
- **API Testing**: Use Postman or curl commands

## 📚 Feature Documentation

For detailed feature documentation, see:
- [`CSV_EXPORT_IMPLEMENTATION.md`](CSV_EXPORT_IMPLEMENTATION.md) - Complete CSV export system guide

## 🤝 Git Workflow

### Branch Management
```bash
# Check current branch
git branch --show-current

# Switch to development branch
git checkout feature/23f1000704-Development

# View changes
git status
git status -s  # Short format

# Stage changes
git add .

# Commit changes
git commit -m "Feature: Add user dashboard with CSV export"

# Push to remote
git push -u origin feature/23f1000704-Development
```

### Configuration
```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

## 🎯 What's Working

- ✅ **Daily Reminders**: Automated email notifications for inactive users
- ✅ **Monthly Reports**: Comprehensive HTML performance reports  
- ✅ **CSV Exports**: On-demand quiz data exports with job tracking
- ✅ **User Dashboard**: Professional interface with real-time updates
- ✅ **Admin Panel**: Complete quiz and user management
- ✅ **Background Jobs**: Celery-based async task processing
- ✅ **Email System**: G-Chat styled HTML email templates

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review log files for error messages
3. Ensure all system components are running
4. Verify environment variables are set correctly

---

## 🚀 **COMPLETE 5-TERMINAL STARTUP GUIDE ========**

Follow these steps to run the complete Distributed Assessment Platform system with all features enabled:

### 📋 **Prerequisites Check**
Before starting, ensure you have:
- Python 3.8+ installed
- Node.js 16+ installed  
- Redis server installed
- Virtual environment created

### 🎯 *********Step-by-Step Terminal Setup =====================================================================**

####  Create virtual environment
```bash
python3 -m venv .env
source .env/bin/activate  # Linux/Mac
```
####  Install dependencies
####  pip freeze > requirements.txt
```bash
cd quiz-master-api
pip install -r requirements.txt
```
###  Frontend Setup
```bash
cd quiz-master-ui

# Install dependencies
npm install

```
#### **Terminal 1: Redis Server** 🔴
```bash
# Start Redis message broker (required for Celery)
source .env/bin/activate
redis-cli ping  # will return pong if running  

redis-server

# Expected output: "Ready to accept connections" 

# Keep this terminal running
```
#### **Terminal 2: Celery Worker** 🟡  
```bash

# Activate Python virtual environment
cd /home/user/mad/distributed-assessment-platform
source .env/bin/activate

# Navigate to API directory
cd /home/user/mad/distributed-assessment-platform/quiz-master-api
# Start Celery worker for background jobs
celery -A app.celery_app worker --loglevel=info

# Expected output: "celery@hostname ready"
# This handles: CSV exports, email sending, report generation
```

#### **Terminal 3: Celery Beat Scheduler** 🟠
```bash
# Activate Python virtual environment
cd /home/user/mad/distributed-assessment-platform
source .env/bin/activate

# Navigate to API directory  
cd /home/user/mad/distributed-assessment-platform/quiz-master-api
# Start Celery Beat scheduler
celery -A app.celery_app beat --loglevel=info

# Expected output: "beat: Starting..."
# This handles: Daily reminders, monthly reports scheduling
```

#### **Terminal 4: Flask API Server** 🟢
```bash

# Activate Python virtual environment
cd /home/user/mad/distributed-assessment-platform
source .env/bin/activate

# Navigate to API directory
cd /home/user/mad/distributed-assessment-platform/quiz-master-api
# Start Flask REST API server
python run.py

# Expected output: "Running on http://127.0.0.1:5000"
# API will be available at: http://localhost:5000
```

#### **Terminal 5: Vue.js Frontend** 🔵
```bash

# Activate Python virtual environment
cd /home/user/mad/distributed-assessment-platform
source .env/bin/activate

# Navigate to UI directory
cd /home/user/mad/distributed-assessment-platform/quiz-master-ui

# Start Vue development server
npm run dev

# Expected output: "Local: http://localhost:5173"
# Frontend will be available at: http://localhost:5173
```

### ✅ **Verification Checklist =====================================================================**

After starting all terminals, verify everything is working:

1. **Redis**: `redis-cli ping` should return `PONG`
2. **Celery Worker**: Should show "ready" message with task list
3. **Celery Beat**: Should show "beat: Starting..." and schedule info
4. **Flask API**: Visit http://localhost:5000 (should show API response)
5. **Vue Frontend**: Visit http://localhost:5173 (should show login page)

### 🎯 **Quick Status Check**
```bash
# Check all running processes
ps aux | grep -E "(redis|celery|python|node)"

# Should show 5 processes running:
# - redis-server
# - celery worker  
# - celery beat
# - python run.py (Flask)
# - node (Vue dev server)
```

### 🔧 **Environment Variables** (Optional but Recommended)
```bash
# Set email configuration for notifications
export IITM_EMAIL_USER="your-email@gmail.com"
export IITM_EMAIL_PASS="your-app-password"

# Verify variables are set
echo $IITM_EMAIL_USER
echo $IITM_EMAIL_PASS
```

### 🎉 **System Ready!**

Once all 5 terminals are running, your complete Distributed Assessment Platform system is operational with:

- ✅ **Daily Reminders**: Automatic email notifications
- ✅ **Monthly Reports**: Scheduled performance reports  
- ✅ **CSV Exports**: On-demand data exports
- ✅ **Real-time UI**: Professional dashboard interface
- ✅ **Background Jobs**: Async task processing

### 🛑 **To Stop the System**
Press `Ctrl+C` in each terminal in reverse order:
1. Terminal 5 (Vue)
2. Terminal 4 (Flask) 
3. Terminal 3 (Celery Beat)
4. Terminal 2 (Celery Worker)
5. Terminal 1 (Redis)

---

**Built with ❤️ for IITM Modern Application Development-II**
