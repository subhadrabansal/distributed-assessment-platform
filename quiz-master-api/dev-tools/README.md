# Development Tools

This directory contains development, testing, and demonstration scripts for the Distributed Assessment Platform application.

## 📋 Testing Scripts

### **`check_reminders.py`**
- **Purpose**: Check reminder logs and user activity status
- **Usage**: `python check_reminders.py`
- **What it shows**: Recent reminder logs, user eligibility for reminders

### **`check_schedule.py`**
- **Purpose**: Display current Celery Beat schedule configuration
- **Usage**: `python check_schedule.py`
- **What it shows**: All scheduled tasks, their timing, and parameters

### **`test_flask_mail.py`**
- **Purpose**: Test Flask-Mail configuration and email sending
- **Usage**: `python test_flask_mail.py`
- **What it tests**: Email server connection, message sending functionality

### **`test_get_response.py`**
- **Purpose**: Test API response formats and endpoints
- **Usage**: `python test_get_response.py`
- **What it tests**: API endpoint responses and data formats

### **`test_manual_reminder.py`**
- **Purpose**: Test manual reminder sending functionality
- **Usage**: `python test_manual_reminder.py`
- **What it tests**: Manual reminder triggers and email delivery

### **`test_otp_email.py`**
- **Purpose**: Test OTP email sending functionality
- **Usage**: `python test_otp_email.py`
- **What it tests**: OTP generation and email delivery

### **`test_settings_api.py`**
- **Purpose**: Test user settings API endpoints
- **Usage**: `python test_settings_api.py`
- **What it tests**: Settings CRUD operations and validation

### **`test_celery_tasks.py`** ⭐ *New*
- **Purpose**: Manual testing of Celery tasks (daily reminders, monthly reports)
- **Usage**: 
  - `python test_celery_tasks.py` - Test both tasks
  - `python test_celery_tasks.py daily` - Test daily reminders only
  - `python test_celery_tasks.py monthly` - Test monthly reports only
  - `python test_celery_tasks.py status <task_id>` - Check task status
- **What it tests**: Celery task execution, email functionality, database logging

### **`test_redis_cache.py`** ⭐ *New*
- **Purpose**: Test Redis cache functionality and invalidation
- **Usage**: `python test_redis_cache.py`
- **What it tests**: Cache status, cache clearing operations, Redis connectivity

### **`monitor_celery_tasks.py`** ⭐ *New*
- **Purpose**: Real-time monitoring of Celery task execution
- **Usage**: `python monitor_celery_tasks.py`
- **What it does**: Watches for scheduled task execution and shows live results

### **`schedule_test.py`** ⭐ *New*
- **Purpose**: Test Celery scheduling with temporary time changes
- **Usage**: 
  - `python schedule_test.py` - Set tasks to run in 2 minutes
  - `python schedule_test.py restore` - Restore original 3:50 AM schedule
- **What it does**: Temporarily modifies schedule for immediate testing

## 🎯 Demo Scripts

### **`demo_csv_export.py`**
- **Purpose**: Demonstrate CSV export functionality
- **Usage**: `python demo_csv_export.py`
- **What it does**: Shows how to export user quiz data to CSV

### **`demo_monthly_reports.py`**
- **Purpose**: Demonstrate monthly report generation
- **Usage**: `python demo_monthly_reports.py`
- **What it does**: Generates sample monthly reports

### **`generate_sample_report.py`**
- **Purpose**: Generate sample reports for testing
- **Usage**: `python generate_sample_report.py`
- **What it does**: Creates sample report data for development

## 🚀 Usage Instructions

### General Usage
1. **Navigate to the project root**:
   ```bash
   cd /path/to/distributed-assessment-platform/quiz-master-api
   ```

2. **Run any script**:
   ```bash
   python dev-tools/script_name.py
   ```

### Celery Testing Workflow
For testing the scheduled notification system:

1. **Manual Testing**:
   ```bash
   python dev-tools/test_celery_tasks.py daily    # Test daily reminders
   python dev-tools/test_celery_tasks.py monthly  # Test monthly reports
   ```

2. **Schedule Testing** (run tasks in 2 minutes):
   ```bash
   python dev-tools/schedule_test.py              # Set test schedule
   python dev-tools/monitor_celery_tasks.py       # Monitor execution
   python dev-tools/schedule_test.py restore      # Restore original schedule
   ```

3. **Real-time Monitoring** (watch for 3:50 AM execution):
   ```bash
   python dev-tools/monitor_celery_tasks.py
   ```

## ⚠️ Important Notes

- These scripts are for **development and testing only**
- They are **not part of the production application**
- Some scripts may require specific environment setup
- Always run from the main project directory, not from within dev-tools/

## 🧹 Maintenance

These tools help with:
- **Debugging** notification systems
- **Testing** email functionality
- **Verifying** scheduled task configurations
- **Demonstrating** export features
- **Validating** API responses

## 📝 Adding New Tools

When adding new development tools:
1. Place them in this directory
2. Add documentation above
3. Use descriptive names with prefixes: `test_`, `check_`, `demo_`, or `generate_`
4. Include proper error handling and help messages
