#!/bin/bash


export TZ='Asia/Kolkata'



echo "🚀 Starting Distributed Assessment Platform Notification & Export System"
echo "=================================================="


check_service() {
    if pgrep -f "$1" > /dev/null; then
        echo "✅ $2 is running"
        return 0
    else
        echo "❌ $2 is not running"
        return 1
    fi
}

start_service() {
    echo "🔄 Starting $2..."
    nohup $1 > $3 2>&1 &
    sleep 2
    if check_service "$4" "$2"; then
        echo "✅ $2 started successfully"
    else
        echo "❌ Failed to start $2"
        exit 1
    fi
}

echo ""
echo "📋 Checking system components..."

if ! check_service "redis-server" "Redis Server"; then
    echo "🔄 Starting Redis Server..."
    redis-server &
    sleep 3
    if ! check_service "redis-server" "Redis Server"; then
        echo "❌ Failed to start Redis. Please install: sudo apt install redis-server"
        exit 1
    fi
fi

echo ""
echo "🔄 Starting Celery components..."

if ! check_service "celery.*worker" "Celery Worker"; then
    start_service "celery -A app.celery_app worker --loglevel=info" "Celery Worker" "logs/celery_worker.log" "celery.*worker"
fi

if ! check_service "celery.*beat" "Celery Beat"; then
    start_service "celery -A app.celery_app beat --loglevel=info" "Celery Beat" "logs/celery_beat.log" "celery.*beat"
fi

echo ""
echo "🌐 Starting Flask Application..."

if ! check_service "python.*run.py" "Flask App"; then
    start_service "python run.py" "Flask App" "logs/flask_app.log" "python.*run.py"
fi

echo ""
echo "🎯 System Status Summary:"
echo "========================"
check_service "redis-server" "Redis Server"
check_service "celery.*worker" "Celery Worker (Background Jobs)"
check_service "celery.*beat" "Celery Beat (Scheduler)"
check_service "python.*run.py" "Flask Application"

echo ""
echo "📊 What's Running:"
echo "- Daily Reminders: Scheduled based on admin settings + user preferences"
echo "- Monthly Reports: 1st of each month at configured time"
echo "- CSV Exports: On-demand via user dashboard"
echo "- Email Notifications: G-Chat styled HTML emails"

echo ""
echo "🔧 Admin Endpoints:"
echo "- POST /api/admin/report/trigger-monthly-reports"
echo "- Admin settings at: /api/admin/settings/"

echo ""
echo "👤 User Endpoints:"
echo "- User Dashboard: /pages/user/Dashboard.vue"
echo "- POST /api/user/export/trigger-csv-export"
echo "- GET /api/user/export/my-exports"

echo ""
echo "📱 Access Points:"
echo "- Frontend: http://localhost:5173 (if Vue dev server is running)"
echo "- Backend API: http://localhost:5000"
echo "- Logs: Check logs/ directory"

echo ""
echo "✅ All systems are operational!"
echo "💡 The system will now automatically:"
echo "   📧 Send daily reminders at user-preferred times"  
echo "   📊 Generate monthly reports on 1st of each month"
echo "   📋 Process CSV exports when users request them"
